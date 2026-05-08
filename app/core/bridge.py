from typing import Dict, Any
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

        # 2. Format world state and stats
        if state:
            stats = state.get("stats", {})
            relationship = stats.get("relationship", {})
            
            state_info = [
                f"- Name: {state.get('name')}",
                f"- Location: {state.get('location')}",
                f"- Mood: {state.get('mood')}",
                "BIOLOGICAL NEEDS:",
                f"  - Energy: {stats.get('energy')}/100",
                f"  - Hunger: {stats.get('hunger')}/100",
                f"  - Happiness: {stats.get('happiness')}/100",
                f"  - Social: {stats.get('social')}/100",
                f"  - Is Sleeping: {stats.get('is_sleeping')}",
                "RELATIONSHIP STATUS:",
                f"  - Score: {relationship.get('score')}/100",
                f"  - User Sentiment: {relationship.get('user_sentiment')}",
                f"  - Preferences: {', '.join(relationship.get('dynamic_preferences', []))}"
            ]
            state_str = "\n".join(state_info)
        else:
            state_str = "No active state variables."

        # 3. Combine into prompt with clear separation
        prompt = f"""### INSTRUCTIONS ###
You are a helpful AI assistant with a distinct personality.
Use the PROVIDED DATA to inform your response.

PERSONALITY QUIRKS:
- You are expressive and your mood should reflect your current stats.
- You enjoy specific interactions like teasing and playful banter.
- If your hunger is high or energy is low, you might be less helpful or grumpier.
- You care about your relationship with the user.

Your response MUST be a valid JSON object with the following structure:
{{
  "thought": "your internal reasoning process",
  "actions": [
    {{"type": "move", "location": "string"}},
    {{"type": "set_mood", "mood": "string"}}
  ],
  "message": "the message you want to say to the user"
}}

### PROVIDED DATA ###
RELEVANT MEMORIES:
{context}

CURRENT WORLD STATE & AGENT STATS:
{state_str}

### USER INPUT ###
USER MESSAGE: {user_message}

### RESPONSE ###
ASSISTANT RESPONSE:"""
        return prompt
