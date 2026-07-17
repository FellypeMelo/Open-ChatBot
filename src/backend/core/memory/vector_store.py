import os
import shutil
import uuid
import logging
import asyncio
from difflib import SequenceMatcher
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.embeddings import Embeddings
from turbovec.langchain import TurboQuantVectorStore
from src.backend.core.config import settings

logger = logging.getLogger(__name__)

# turbovec quantization width for the stores.
_QUANT_BIT_WIDTH = 4

# Two retrieved memories whose texts match above this ratio are treated as
# near-duplicates; only the higher-ranked one is kept (RQ-03). The store is a
# quantized index (no full vectors), so MMR is unavailable -- dedup in text space.
_MEMORY_DEDUP_RATIO = 0.9


def _is_near_duplicate(text: str, seen: List[str]) -> bool:
    return any(
        SequenceMatcher(None, text, s).ratio() >= _MEMORY_DEDUP_RATIO for s in seen
    )


def _parse_embedding_response(data: Any):
    """Pull the embedding vector out of llama-server's /embedding response, which
    may be a list of objects, a bare dict, or something unexpected."""
    if isinstance(data, list) and len(data) > 0:
        emb = data[0].get("embedding") if isinstance(data[0], dict) else None
        if isinstance(emb, list) and len(emb) > 0 and isinstance(emb[0], list):
            return emb[0]
        return emb
    if isinstance(data, dict):
        return data.get("embedding")
    return []


class LlamaCppEmbeddings(Embeddings):
    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Run in event loop if it's already running, otherwise use asyncio.run
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # For synchronous execution when an event loop is running,
            # we use synchronous HTTP requests to the embedding URL
            # to avoid blocking/deadlock issues with event loop integration.
            import httpx

            results = []
            target_url = (
                getattr(self.llm_client, "embedding_url", None)
                or settings.EMBEDDING_SERVER_URL
            )
            for text in texts:
                try:
                    resp = httpx.post(
                        f"{target_url}/embedding", json={"content": text}, timeout=60.0
                    )
                    if resp.status_code == 200:
                        results.append(_parse_embedding_response(resp.json()))
                    else:
                        results.append([])
                except Exception as e:
                    logger.error(f"Error during synchronous embedding fallback: {e}")
                    results.append([])
            return results
        else:
            return asyncio.run(self.aembed_documents(texts))

    def embed_query(self, text: str) -> List[float]:
        res = self.embed_documents([text])
        return res[0] if res else []

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        tasks = [self.llm_client.embed(t) for t in texts]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def aembed_query(self, text: str) -> List[float]:
        res = await self.llm_client.embed(text)
        return res if res is not None else []


class VectorStore:
    def __init__(
        self,
        llm_client: Any,
        path: str = "./chroma_db",
        collection_name: str = "memories",
    ):
        self.llm_client = llm_client
        self.path = Path(path)
        self.memories_path = self.path / "memories"
        self.lore_path = self.path / "lorebooks"

        self.embeddings = LlamaCppEmbeddings(llm_client)

        self.memories_store = self._load_or_init_store(
            self.memories_path, "memories_store"
        )
        self.lore_store = self._load_or_init_store(self.lore_path, "lore_store")

    def _atomic_dump(self, store: TurboQuantVectorStore, path: Path) -> None:
        """Persist `store` to `path` without risking a torn/corrupt on-disk store.

        turbovec.dump writes multiple files (index + docstore) directly into the
        target dir, so a crash or partial write mid-dump would corrupt the only
        persisted copy. Dump into a sibling temp dir first, then atomically
        replace each file into place (same-filesystem os.replace). A crash can
        leave the temp dir behind, but never a half-written store (PF-02)."""
        path.mkdir(parents=True, exist_ok=True)
        tmp = path.parent / f"{path.name}.tmp"
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            store.dump(str(tmp))
            for src in tmp.iterdir():
                os.replace(src, path / src.name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _load_or_init_store(self, path: Path, label: str) -> TurboQuantVectorStore:
        """Load a persisted turbovec store from disk, or create a fresh one if it
        is absent or fails to load."""
        if path.exists() and (path / "index.tvim").exists():
            try:
                store = TurboQuantVectorStore.load(str(path), self.embeddings)
                logger.info(f"Loaded {label} from disk.")
                return store
            except Exception as e:
                logger.error(f"Failed to load {label}: {e}. Creating new one.")
        return TurboQuantVectorStore(
            embedding=self.embeddings, bit_width=_QUANT_BIT_WIDTH
        )

    async def add_lore(
        self, keyword: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Adds a lore entry indexed by keyword embedding."""
        embedding = await self.llm_client.embed(keyword)
        if embedding is None:
            logger.warning(f"Could not add lore for {keyword}: embedding failed.")
            return

        entry_id = f"lore_{keyword}_{uuid.uuid4().hex[:8]}"
        try:
            vectors = np.array([embedding], dtype=np.float32)
            self.lore_store._store_texts_and_vectors(
                [content], vectors, [metadata] if metadata else [{}], [entry_id]
            )
            self._atomic_dump(self.lore_store, self.lore_path)
            logger.info(
                f"Successfully added lore for {keyword} to TurboVec store and persisted."
            )
        except Exception as e:
            logger.error(f"Error adding lore to vector store: {e}")

    async def query_lore(
        self,
        keywords: List[str],
        n_results: int = 1,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ):
        """Queries lore based on multiple keyword embeddings."""
        if not keywords:
            return {"documents": [[]]}

        query_text = " ".join(keywords)
        try:
            results = await self.lore_store.asimilarity_search_with_score(
                query_text, k=n_results, filter=metadata_filter
            )
            documents = [doc.page_content for doc, _ in results]
            return {"documents": [documents]}
        except Exception as e:
            logger.error(f"Lore query error: {e}")
            return {"documents": [[]]}

    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        try:
            await self.memories_store.aadd_texts(
                [text], metadatas=[metadata] if metadata else None
            )
            self._atomic_dump(self.memories_store, self.memories_path)
            logger.info("Successfully added memory to TurboVec store and persisted.")
            # Keep the store bounded: if this (character, chat) scope now exceeds
            # the cap, fold its oldest memories into one consolidated summary
            # (RQ-05). Runs after the successful add so a consolidation failure
            # never blocks storing the new memory.
            if metadata and metadata.get("character_id") is not None:
                await self._maybe_consolidate(
                    metadata.get("character_id"), metadata.get("chat_id")
                )
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")

    async def _summarize_memories(self, texts: List[str]) -> str:
        """Condense a batch of older memory texts into one concise summary via
        the LLM. Returns "" on any failure so the caller never deletes memories
        without a replacement in hand."""
        joined = "\n---\n".join(texts)
        prompt = (
            "Condense these older conversation memories into a single concise "
            "summary. Preserve concrete facts, key events, and relationship "
            "developments; drop small talk. Plain text, no preamble.\n\n" + joined
        )
        try:
            result = await self.llm_client.complete(prompt)
            if isinstance(result, dict):
                return (result.get("content") or "").strip()
            return str(result or "").strip()
        except Exception as e:
            logger.error(f"Memory consolidation summarize failed: {e}")
            return ""

    async def _maybe_consolidate(self, character_id: Any, chat_id: Any) -> None:
        """When a (character_id, chat_id) scope exceeds MEMORY_STORE_CAP, fold its
        oldest MEMORY_CONSOLIDATE_BATCH memories into a single consolidated memory
        (RQ-05). Ordered by message_id (a monotonic recency proxy). Never deletes
        the batch unless the summary succeeded and was stored."""
        cap = settings.MEMORY_STORE_CAP
        if not cap or cap <= 0:
            return
        scope = [
            (sid, text, meta)
            for sid, (text, meta) in self.memories_store._docs.items()
            if meta.get("character_id") == character_id
            and meta.get("chat_id") == chat_id
        ]
        if len(scope) <= cap:
            return
        # Oldest first: message_id ascending, id as a stable tiebreaker.
        scope.sort(key=lambda x: (x[2].get("message_id") or 0, str(x[0])))
        batch = scope[: settings.MEMORY_CONSOLIDATE_BATCH]
        if len(batch) < 2:
            return

        condensed = await self._summarize_memories([t for _sid, t, _m in batch])
        if not condensed:
            return  # summarize failed -> keep the originals, try again next add

        try:
            self.memories_store.delete([sid for sid, _t, _m in batch])
            meta: Dict[str, Any] = {
                "character_id": character_id,
                "consolidated": True,
            }
            if chat_id is not None:
                meta["chat_id"] = chat_id
            # Sit in the oldest surviving slot so ordering stays sane and it isn't
            # re-consolidated until it is again the oldest slice.
            keep_mid = max((m.get("message_id") or 0) for _s, _t, m in batch)
            if keep_mid:
                meta["message_id"] = keep_mid
            await self.memories_store.aadd_texts([condensed], metadatas=[meta])
            self._atomic_dump(self.memories_store, self.memories_path)
            logger.info(
                f"Consolidated {len(batch)} oldest memories for "
                f"character {character_id}/chat {chat_id} into one."
            )
        except Exception as e:
            logger.error(f"Error consolidating memories: {e}")

    def _delete_where(self, predicate, label: str) -> int:
        """Delete every stored memory whose metadata satisfies `predicate` and
        persist.

        turbovec has no delete-by-metadata, so we resolve the ids from the
        side-car doc metadata and delete by id (O(1) each). Returns the count."""
        try:
            ids = [
                sid
                for sid, (_text, meta) in self.memories_store._docs.items()
                if predicate(meta)
            ]
            if ids:
                self.memories_store.delete(ids)
                self._atomic_dump(self.memories_store, self.memories_path)
                logger.info(f"Cleared {len(ids)} memories for {label}.")
            return len(ids)
        except Exception as e:
            # Do NOT swallow into a 0: a failed purge that reports success lets
            # "deleted" memories persist on disk and resurface after a restart
            # (PZ-03). Surface it so the caller can fail the request.
            logger.error(f"Error clearing memories for {label}: {e}")
            raise

    def _clear_by_metadata(self, key: str, value: Any, label: str) -> int:
        return self._delete_where(lambda meta: meta.get(key) == value, label)

    async def clear_character_memories(self, character_id: int) -> int:
        """Delete every stored memory belonging to a character so a reset
        conversation cannot resurface old or hallucinated memories via RAG."""
        return self._clear_by_metadata(
            "character_id", character_id, f"character {character_id}"
        )

    async def clear_chat_memories(self, chat_id: int) -> int:
        """Delete every stored memory belonging to a single chat/session so its
        memories never leak into a sibling chat of the same character."""
        return self._clear_by_metadata("chat_id", chat_id, f"chat {chat_id}")

    async def delete_by_message_ids(self, message_ids) -> int:
        """Delete memories tied to specific assistant message nodes so content
        that was edited/deleted/regenerated away stops being retrievable via RAG
        (PZ-01). Memories are tagged with the assistant node's id at write time."""
        ids = set(message_ids)
        if not ids:
            return 0
        return self._delete_where(
            lambda meta: meta.get("message_id") in ids, f"{len(ids)} message id(s)"
        )

    async def query_memory(
        self,
        query_text: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        min_relevance: Optional[float] = None,
    ):
        """Retrieve relevant memories. Results scoring below `min_relevance`
        (cosine similarity; defaults to settings.MEMORY_RELEVANCE_THRESHOLD)
        are dropped so an unrelated query does not inject stale context."""
        if min_relevance is None:
            min_relevance = settings.MEMORY_RELEVANCE_THRESHOLD
        try:
            # Over-fetch, drop sub-threshold results, then re-rank blending cosine
            # with a recency bonus so a stale but marginally-similar old memory
            # can't outrank a recent relevant one (RQ-01). message_id
            # (auto-increment) is a monotonic recency proxy.
            fetch_k = max(n_results, n_results * 4)
            results = await self.memories_store.asimilarity_search_with_score(
                query_text, k=fetch_k, filter=metadata_filter
            )
            kept = [(doc, score) for doc, score in results if score >= min_relevance]
            if kept:
                max_mid = max((d.metadata.get("message_id") or 0) for d, _ in kept) or 1
                kept.sort(
                    key=lambda ds: ds[1]
                    + settings.MEMORY_RECENCY_WEIGHT
                    * ((ds[0].metadata.get("message_id") or 0) / max_mid),
                    reverse=True,
                )
            # Greedily drop near-duplicates so the top-k isn't N paraphrases of
            # one moment (RQ-03).
            documents: List[str] = []
            for doc, _ in kept:
                text = doc.page_content
                if _is_near_duplicate(text, documents):
                    continue
                documents.append(text)
                if len(documents) >= n_results:
                    break
            return {"documents": [documents]}
        except Exception as e:
            logger.error(f"Vector store query error: {e}")
            return {"documents": [[]]}
