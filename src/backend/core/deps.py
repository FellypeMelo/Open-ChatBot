"""Composition root: the app-wide singletons every router shares.

Each router used to build its own LlamaClient/VectorStore/Brain, which meant
three separate HTTP connection pools and three independent in-memory vector
stores pointed at the same chroma_db path -- a memory or lore entry added
through one router's instance was invisible to another's until a restart.
Constructing them once here and importing from here everywhere keeps the app
in sync with itself.
"""

from src.backend.core.engine.llm import LlamaClient
from src.backend.core.memory.vector_store import VectorStore
from src.backend.core.orchestration.bridge import Brain

llama_client = LlamaClient()
vector_store = VectorStore(llm_client=llama_client)
brain = Brain(vector_store=vector_store)


def get_llama_client() -> LlamaClient:
    return llama_client


def get_vector_store() -> VectorStore:
    return vector_store


def get_brain() -> Brain:
    return brain
