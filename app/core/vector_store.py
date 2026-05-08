import chromadb
import uuid
from typing import List, Dict, Any, Optional

class VectorStore:
    def __init__(self, llm_client: Any, path: str = "./chroma_db", collection_name: str = "memories"):
        self.llm_client = llm_client
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        embedding = await self.llm_client.embed(text)
        # ChromaDB expects a list of IDs, we can use a hash or just an incremental ID
        memory_id = str(uuid.uuid4())
        
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata] if metadata else None
        )

    async def query_memory(self, query_text: str, n_results: int = 5, metadata_filter: Optional[Dict[str, Any]] = None):
        query_embedding = await self.llm_client.embed(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=metadata_filter
        )
        return results
