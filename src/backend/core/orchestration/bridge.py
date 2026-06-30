import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.backend.core.memory.vector_store import VectorStore
from src.backend.db.models import Tag
from langchain_core.prompts import PromptTemplate
from src.backend.core.context.compressor import COMPRESSED_MASTER_PROMPT, compress_state
from src.backend.core.context.budget import ContextBudgetCalculator

logger = logging.getLogger(__name__)

REFLECTION_GRAMMAR = r'''
root ::= "{" space "\"summary\"" ":" space string "," space "\"facts\"" ":" space list "," space "\"traits\"" ":" space list "," space "\"relationship_change\"" ":" space number "," space "\"diary_entry\"" ":" space string space "}"
list ::= "[" space (string ("," space string)*)? space "]"
string ::= "\"" ([^"\\] | "\\" ["\\/bfnrt] | "\\u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])* "\""
number ::= "-"? [0-9]+
space ::= [ \t\n\r]*
'''

# The ultra-compact Prompt Template (Plain Text, no redundant markdown headers)
ENTITY_PROMPT_TEMPLATE = PromptTemplate.from_template(
    "{master_prompt}\n\n"
    "Identity: {identity}\n"
    "{modifiers}\n"
    "{user_persona}\n"
    "{state_str}\n\n"
    "Memories:\n{context}{lore_context}\n"
    "{summary_context}\n"
    "History:\n{history_str}\n\n"
    "{user_info}: {user_message}\n\n"
    "Reply:"
)

class Brain:
    def __init__(self, vector_store: VectorStore, llm_client=None):
        self.vector_store = vector_store
        self.llm = llm_client or vector_store.llm_client
        self.budget_calc = ContextBudgetCalculator(llama_url=self.llm.base_url if hasattr(self.llm, 'base_url') else "http://127.0.0.1:8080")

    async def build_prompt(self, user_message: str, character: Any, state: Dict[str, Any], user: Any = None, history: List[Any] = None, db: Session = None) -> str:
        """Assembles the ultra-compact 6-layer prompt for models 1-4B using Token Budgeting."""
        budget = await self.budget_calc.get_budget()
        
        # Layer 1: Memories (RAG)
        context_data = await self.vector_store.query_memory(user_message, metadata_filter={"character_id": character.id} if character else None)
        context = "None."
        if isinstance(context_data, dict) and context_data.get("documents"):
            docs = context_data["documents"][0]
            if docs: context = " ".join([str(d) for d in docs if d])

        # Layer 1.5: Lorebooks (Keyword-triggered via Regex Scanner V2)
        lore_context = ""
        if db and character:
            from src.backend.core.context.lorebook_scanner import LorebookScanner
            scanner = LorebookScanner(db)
            active_lore = scanner.scan_and_extract(user_message, character.id)
            if active_lore:
                lore_context = "\nLore:\n" + "\n".join([f"- {d}" for d in active_lore])

        # Layer 1.5: Summary
        active_summary = state.get("active_summary", "") if state else ""
        summary_context = f"\nSummary:\n{active_summary}\n" if active_summary else ""

        # Layer 2: History (Dynamic Sliding Window)
        user_name = user.name if user else "User"
        char_name = character.name if character else "You"
        
        history_lines = []
        if history:
            for msg in history:
                role_val = msg['role'] if isinstance(msg, dict) else getattr(msg, 'role', '')
                role = user_name if role_val == "user" else char_name
                content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
                history_lines.append(f"{role}: {content}")
        
        # Enforce budget for history
        history_str = ""
        if history_lines:
            history_budget = budget.get("history_budget", 2048) # Default fallback
            current_tokens = 0
            allowed_lines = []
            
            # Start from the most recent (end of list) and go backwards
            for line in reversed(history_lines):
                # Approximation for speed: 1 token ~ 4 chars
                est_tokens = len(line) // 4 + 5
                if current_tokens + est_tokens <= history_budget:
                    allowed_lines.insert(0, line)
                    current_tokens += est_tokens
                else:
                    break
            history_str = "\n".join(allowed_lines)

        # Layer 3: Identity & Tags & Persona
        identity = f"{character.name}. {character.description}" if character else "You are unique."
        tags = []
        if character and character.tags:
            for t in character.tags: tags.append(f"[{t.label}]: {t.instruction}")
            
        user_persona = ""
        if user:
            persona_parts = []
            if user.gender and user.gender != "Unknown": persona_parts.append(f"Gender: {user.gender}")
            if getattr(user, 'appearance', None): persona_parts.append(f"Appearance: {user.appearance}")
            if getattr(user, 'persona_description', None): persona_parts.append(f"Persona: {user.persona_description}")
            if persona_parts:
                user_persona = f"User ({user_name}): " + " | ".join(persona_parts)
        
        # Layer 4: State (Compressed)
        state_str = compress_state(state, user_name)

        # Format via LangChain PromptTemplate
        return ENTITY_PROMPT_TEMPLATE.format(
            master_prompt=COMPRESSED_MASTER_PROMPT,
            identity=identity,
            modifiers="\n".join(tags),
            user_persona=user_persona,
            state_str=state_str,
            context=context,
            lore_context=lore_context,
            summary_context=summary_context,
            history_str=history_str,
            user_info=user_name,
            user_message=user_message
        )

    async def reflect(self, messages: List[Dict], window_size: int = 20) -> Dict:
        """Analyzes interaction for summary, facts, traits, relationship change, and diary entry."""
        prompt = (
            "Analyze the interaction. Extract a summary, new facts about the user, character trait updates, "
            "a relationship_change integer (ranging from -5 to +5) representing how much the user's bonding progress "
            "improved or declined based on their tone (positive/friendly = positive change, hostile/cold = negative change), "
            "and a 'diary_entry' string containing a 2-3 sentence diary entry written in the first person from the character's "
            "perspective. The diary entry must express their raw inner thoughts, emotional state, insecurities, or feelings of closeness "
            "regarding the user based on these recent interactions. JSON ONLY.\n\n"
        )
        for msg in messages[-window_size:]:
            role = msg['role'].capitalize() if isinstance(msg, dict) else getattr(msg, 'role', '').capitalize()
            content = msg['content'] if isinstance(msg, dict) else getattr(msg, 'content', '')
            prompt += f"{role}: {content}\n"
        
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
