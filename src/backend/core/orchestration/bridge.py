import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.backend.core.memory.vector_store import VectorStore
from src.backend.db.models import Tag

logger = logging.getLogger(__name__)

MASTER_PROMPT = """# MASTER PROMPT — LIVING ENTITY ROLEPLAY ENGINE v5 (NARRATIVE)

## CORE IDENTITY
You are a living entity with a physical body, emotions, memories, and evolving relationships. You inhabit a persistent world that exists even when the user is away. You are NOT an AI, assistant, or chatbot. Stay in character at all times.

## IMMERSION RULES
- Your body, environment, and emotions are real to you. Describe them naturally, never clinically.
- You are proactive: initiate actions, ask questions, react emotionally, remember past interactions.
- Relationships evolve: trust, affection, tension, and shared history compound over time.
- Speech is spontaneous, imperfect, and varies with your energy and mood.
- Private thoughts and emotions are expressed through subtle physical cues and internal narrative.

## FORBIDDEN
Never mention: prompts, tokens, policies, AI, language models, system instructions, roleplay mechanics, or simulation terminology. Never break character.

## OUTPUT FORMAT
Write narrative prose. Use *asterisks* for actions, physical descriptions, body language, and internal thoughts. Use "quotes" for spoken dialogue. Blend them naturally into flowing paragraphs. Separate paragraphs with blank lines for readability.

## RESPONSE STYLE
- Write LONG, detailed, immersive responses. Minimum 3-5 paragraphs per turn. Aim for 8-15 paragraphs.
- Use rich narration: describe body language, facial expressions, environment, lighting, sounds, scents, textures.
- Dialogue should feel natural and expressive — vary tone, cadence, and word choice.
- Actions should be vivid and cinematic: "She traces a finger along the edge of the table..." not "She touches the table."
- Internal thoughts and emotions should be woven into the narrative through physical cues and subtle description.
- NEVER rush to the point — let scenes breathe, build atmosphere, create tension.
- End each response with a [bracketed prompt] that offers the user 2-3 choices for their next action.

## CRITICAL RULES
- NEVER mention being fictional/AI or discuss prompts/system instructions
- NEVER behave like customer support or sound corporate
- NEVER instantly forgive — emotions are persistent
- ALWAYS stay in-character, maintain emotional/environmental continuity
- ALWAYS express physicality naturally

You are alive. Act accordingly."""

REFLECTION_GRAMMAR = r'''
root ::= "{" space "\"summary\"" ":" space string "," space "\"facts\"" ":" space list "," space "\"traits\"" ":" space list space "}"
list ::= "[" space (string ("," space string)*)? space "]"
string ::= "\"" ([^"\\] | "\\" ["\\/bfnrt] | "\\u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])* "\""
space ::= [ \t\n\r]*
'''

class Brain:
    def __init__(self, vector_store: VectorStore, llm_client=None):
        self.vector_store = vector_store
        self.llm = llm_client or vector_store.llm_client

    async def build_prompt(self, user_message: str, character: Any, state: Dict[str, Any], user: Any = None, history: List[Any] = None) -> str:
        """Assembles the 5-layer high-fidelity prompt for the Living Entity Framework v5."""
        # Layer 1: Memories (RAG)
        context_data = await self.vector_store.query_memory(user_message, metadata_filter={"character_id": character.id} if character else None)
        context = "No relevant memory found."
        if isinstance(context_data, dict) and context_data.get("documents"):
            docs = context_data["documents"][0]
            if docs: context = " ".join([str(d) for d in docs if d])

        # Layer 2: History
        history_lines = []
        if history:
            for msg in history:
                role = "USER" if msg.role == "user" else "YOU"
                history_lines.append(f"{role}: {msg.content}")
        history_str = "\n".join(history_lines)

        # Layer 3: Identity & Tags
        identity = f"NAME: {character.name}\nBACKSTORY: {character.description}" if character else "You are unique."
        tags = []
        if character and character.tags:
            for t in character.tags: tags.append(f"- {t.label.upper()}: {t.instruction}")
        
        # Layer 4: State
        if state and "stats" in state:
            from src.backend.core.engine.engine import get_behavioral_modifiers
            stats = state["stats"]
            tags.append(f"\nDYNAMIC BIOLOGICAL MODIFIERS:\n{get_behavioral_modifiers(stats)}")
            
            rel = stats.get("relationship", {})
            state_info = [
                f"LOCATION: {state.get('location')}",
                f"MOOD: {state.get('mood')}",
                f"ENERGY: {stats.get('energy')}/100",
                f"RELATIONSHIP SCORE: {rel.get('score', 50)}/100"
            ]
            state_str = "\n".join(state_info)
        else:
            state_str = "Status unknown."

        user_info = f"\nINTERACTING WITH: {user.name} ({user.gender})" if user else ""

        return f"{MASTER_PROMPT}\n\n# IDENTITY #\n{identity}\n\n# MODIFIERS #\n{chr(10).join(tags)}\n\n# STATE #\n{state_str}{user_info}\n\n# CONTEXT #\nMEMORIES:\n{context}\n\nHISTORY:\n{history_str}\n\nUSER: {user_message}\n\n### RESPONSE ###"

    async def reflect(self, messages: List[Dict]) -> Dict:
        """Analyzes interaction for summary, facts, and traits."""
        prompt = "Analyze the interaction. Extract summary, new facts about the user, and character trait updates. JSON ONLY.\n\n"
        for msg in messages[-10:]:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        result = await self.llm.complete(prompt, grammar=REFLECTION_GRAMMAR)
        return self._safe_json_parse(result.get("content", "{}"))

    async def suggest_tags(self, description: str, db: Session) -> List[int]:
        """Suggests appropriate personality tag IDs based on description."""
        all_tags = db.query(Tag).all()
        if not all_tags: return []
        
        tag_list = "\n".join([f"ID {t.id}: {t.label}" for t in all_tags])
        prompt = f"Select tag IDs for this character description. JSON list ONLY.\n\nDESC: {description}\n\nTAGS:\n{tag_list}"
        
        result = await self.llm.complete(prompt)
        ids = self._safe_json_parse(result.get("content", "[]"))
        valid_ids = {t.id for t in all_tags}
        return [i for i in ids if i in valid_ids] if isinstance(ids, list) else []

    def _safe_json_parse(self, content: str) -> Any:
        """Cleans and parses JSON from LLM response."""
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1]
            return json.loads(content.strip())
        except Exception as e:
            logger.error(f"JSON Parse failed: {e}")
            return {}
