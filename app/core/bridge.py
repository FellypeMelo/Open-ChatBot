from typing import Dict, Any
from app.core.llm import LlamaClient
from app.core.vector_store import VectorStore

class Brain:
    def __init__(self, llm: LlamaClient, vector_store: VectorStore):
        self.llm = llm
        self.vector_store = vector_store

    async def build_prompt(self, user_message: str, state: Dict[str, Any]) -> str:
        # 1. Query VectorStore for context
        context_data = await self.vector_store.query_memory(user_message)
        documents = context_data.get("documents", [[]])
        context = " ".join(documents[0]) if documents and documents[0] else "No relevant memory found."

        # 2. Format world state
        state_str = "\n".join([f"- {k}: {v}" for k, v in state.items()])

        # 3. Combine into prompt
        prompt = f"""System Context:
Relevant Memories: {context}

Current World State:
{state_str}

User Message: {user_message}

Assistant Response:"""
        return prompt
