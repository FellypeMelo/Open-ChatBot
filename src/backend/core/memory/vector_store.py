import uuid
import logging
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.embeddings import Embeddings
from turbovec.langchain import TurboQuantVectorStore
from src.backend.core.config import settings

logger = logging.getLogger(__name__)

# turbovec quantization width for the stores.
_QUANT_BIT_WIDTH = 4


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
            self.lore_path.mkdir(parents=True, exist_ok=True)
            self.lore_store.dump(str(self.lore_path))
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
            self.memories_path.mkdir(parents=True, exist_ok=True)
            self.memories_store.dump(str(self.memories_path))
            logger.info("Successfully added memory to TurboVec store and persisted.")
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")

    def _clear_by_metadata(self, key: str, value: Any, label: str) -> int:
        """Delete every stored memory whose metadata[key] == value and persist.

        turbovec has no delete-by-metadata, so we resolve the ids from the
        side-car doc metadata and delete by id (O(1) each). Returns the count."""
        try:
            ids = [
                sid
                for sid, (_text, meta) in self.memories_store._docs.items()
                if meta.get(key) == value
            ]
            if ids:
                self.memories_store.delete(ids)
                self.memories_path.mkdir(parents=True, exist_ok=True)
                self.memories_store.dump(str(self.memories_path))
                logger.info(f"Cleared {len(ids)} memories for {label}.")
            return len(ids)
        except Exception as e:
            logger.error(f"Error clearing memories for {label}: {e}")
            return 0

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
            results = await self.memories_store.asimilarity_search_with_score(
                query_text, k=n_results, filter=metadata_filter
            )
            documents = [
                doc.page_content for doc, score in results if score >= min_relevance
            ]
            return {"documents": [documents]}
        except Exception as e:
            logger.error(f"Vector store query error: {e}")
            return {"documents": [[]]}
