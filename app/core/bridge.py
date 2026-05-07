from typing import Dict, Any
from app.core.llm import LlamaClient
from app.core.vector_store import VectorStore

class Brain:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def build_prompt(self, user_message: str, state: Dict[str, Any]) -> str:
        # 1. Query VectorStore for context
        context_data = await self.vector_store.query_memory(user_message)
        
        # Robust handling for nested list structure from VectorStore
        context = "No relevant memory found."
        if isinstance(context_data, dict):
            documents = context_data.get("documents")
            if isinstance(documents, list) and len(documents) > 0:
                first_doc_list = documents[0]
                if isinstance(first_doc_list, list) and len(first_doc_list) > 0:
                    context = " ".join([str(doc) for doc in first_doc_list if doc])

        # 2. Format world state
        if state:
            state_str = "\n".join([f"- {k}: {v}" for k, v in state.items()])
        else:
            state_str = "No active state variables."

        # 3. Combine into prompt with clear separation
        prompt = f"""### INSTRUCTIONS ###
You are a helpful AI assistant. Use the PROVIDED DATA to inform your response.

### PROVIDED DATA ###
RELEVANT MEMORIES:
{context}

CURRENT WORLD STATE:
{state_str}

### USER INPUT ###
USER MESSAGE: {user_message}

### RESPONSE ###
ASSISTANT RESPONSE:"""
        return prompt
