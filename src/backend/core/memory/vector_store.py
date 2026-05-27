import chromadb
import uuid
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, llm_client: Any, path: str = "./chroma_db", collection_name: str = "memories"):
        self.llm_client = llm_client
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.lore_collection = self.client.get_or_create_collection(name="lorebooks")

    async def add_lore(self, keyword: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Adds a lore entry indexed by keyword embedding."""
        embedding = await self.llm_client.embed(keyword)
        if embedding is None:
            logger.warning(f"Could not add lore for {keyword}: embedding failed.")
            return

        entry_id = f"lore_{keyword}_{uuid.uuid4().hex[:8]}"
        try:
            self.lore_collection.add(
                ids=[entry_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata] if metadata else None
            )
        except Exception as e:
            logger.error(f"Error adding lore to vector store: {e}")

    async def query_lore(self, keywords: List[str], n_results: int = 1, metadata_filter: Optional[Dict[str, Any]] = None):
        """Queries lore based on multiple keyword embeddings."""
        if not keywords: return {"documents": [[]]}
        
        # Combine keywords for a single query or query multiple times?
        # Simple approach: embed the concatenated keywords
        query_text = " ".join(keywords)
        query_embedding = await self.llm_client.embed(query_text)
        if query_embedding is None: return {"documents": [[]]}

        try:
            return self.lore_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=metadata_filter
            )
        except Exception as e:
            logger.error(f"Lore query error: {e}")
            return {"documents": [[]]}

    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        embedding = await self.llm_client.embed(text)
        if embedding is None:
            logger.warning("Could not add memory: embedding generation failed.")
            return

        memory_id = str(uuid.uuid4())
        
        try:
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata] if metadata else None
            )
        except Exception as e:
            if "dimension" in str(e).lower():
                logger.error(f"Vector store dimension mismatch in add_memory: {e}. Resetting chroma_db directory is recommended.")
            else:
                logger.error(f"Error adding to vector store: {e}")

    async def query_memory(self, query_text: str, n_results: int = 5, metadata_filter: Optional[Dict[str, Any]] = None):
        query_embedding = await self.llm_client.embed(query_text)
        if query_embedding is None:
            logger.warning("Memory query skipped: embedding generation failed.")
            return {"documents": [[]]} # Return empty results format

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=metadata_filter
            )
            return results
        except Exception as e:
            if "dimension" in str(e).lower():
                logger.error(f"Vector store dimension mismatch: {e}. You may need to reset the chroma_db directory.")
            else:
                logger.error(f"Vector store query error: {e}")
            return {"documents": [[]]}
