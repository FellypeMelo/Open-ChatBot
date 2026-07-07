import uuid
import logging
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.embeddings import Embeddings
from turbovec.langchain import TurboQuantVectorStore

logger = logging.getLogger(__name__)


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
                or "http://127.0.0.1:8081"
            )
            for text in texts:
                try:
                    resp = httpx.post(
                        f"{target_url}/embedding", json={"content": text}, timeout=60.0
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list) and len(data) > 0:
                            emb = (
                                data[0].get("embedding")
                                if isinstance(data[0], dict)
                                else None
                            )
                            results.append(
                                emb[0]
                                if isinstance(emb, list)
                                and len(emb) > 0
                                and isinstance(emb[0], list)
                                else emb
                            )
                        elif isinstance(data, dict):
                            results.append(data.get("embedding"))
                        else:
                            results.append([])
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

        # Load or initialize memories_store
        if self.memories_path.exists() and (self.memories_path / "index.tvim").exists():
            try:
                self.memories_store = TurboQuantVectorStore.load(
                    str(self.memories_path), self.embeddings
                )
                logger.info("Loaded memories_store from disk.")
            except Exception as e:
                logger.error(f"Failed to load memories_store: {e}. Creating new one.")
                self.memories_store = TurboQuantVectorStore(
                    embedding=self.embeddings, bit_width=4
                )
        else:
            self.memories_store = TurboQuantVectorStore(
                embedding=self.embeddings, bit_width=4
            )

        # Load or initialize lore_store
        if self.lore_path.exists() and (self.lore_path / "index.tvim").exists():
            try:
                self.lore_store = TurboQuantVectorStore.load(
                    str(self.lore_path), self.embeddings
                )
                logger.info("Loaded lore_store from disk.")
            except Exception as e:
                logger.error(f"Failed to load lore_store: {e}. Creating new one.")
                self.lore_store = TurboQuantVectorStore(
                    embedding=self.embeddings, bit_width=4
                )
        else:
            self.lore_store = TurboQuantVectorStore(
                embedding=self.embeddings, bit_width=4
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
            logger.info(f"Successfully added memory to TurboVec store and persisted.")
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")

    async def query_memory(
        self,
        query_text: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ):
        try:
            results = await self.memories_store.asimilarity_search_with_score(
                query_text, k=n_results, filter=metadata_filter
            )
            documents = [doc.page_content for doc, _ in results]
            return {"documents": [documents]}
        except Exception as e:
            logger.error(f"Vector store query error: {e}")
            return {"documents": [[]]}
