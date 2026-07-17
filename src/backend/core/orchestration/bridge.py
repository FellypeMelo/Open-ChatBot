import json
import logging
import re
from difflib import SequenceMatcher
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.backend.core.memory.vector_store import VectorStore
from src.backend.db.models import Tag
from langchain_core.prompts import PromptTemplate
from src.backend.core.context.compressor import COMPRESSED_MASTER_PROMPT, compress_state
from src.backend.core.context.budget import ContextBudgetCalculator
from src.backend.core.context.macros import render_macros

logger = logging.getLogger(__name__)

REFLECTION_GRAMMAR = r"""
root ::= "{" space "\"summary\"" ":" space string "," space "\"facts\"" ":" space list "," space "\"traits\"" ":" space list "," space "\"relationship_change\"" ":" space number "," space "\"diary_entry\"" ":" space string space "}"
list ::= "[" space (string ("," space string)*)? space "]"
string ::= "\"" ([^"\\] | "\\" ["\\/bfnrt] | "\\u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])* "\""
number ::= "-"? [0-9]+
space ::= [ \t\n\r]*
"""

# The ultra-compact Prompt Template (Plain Text, no redundant markdown headers)
ENTITY_PROMPT_TEMPLATE = PromptTemplate.from_template(
    "{master_prompt}\n\n"
    "Identity: {identity}\n"
    "{persona_str}"
    "{scenario_str}"
    "{modifiers}\n"
    "{user_persona}\n"
    "{state_str}\n\n"
    "Memories:\n{context}{lore_context}\n"
    "{summary_context}\n"
    "{example_dialogs_str}"
    "History:\n{history_str}\n\n"
    "{user_info}: {user_message}\n\n"
    "Reply:"
)


_MEMORY_REDUNDANT_RATIO = 0.9


def _norm(text: Any) -> str:
    """Lowercase + collapse whitespace, for cheap text-overlap checks."""
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def _memory_redundant_with_recent(doc: str, recent_lines: List[str]) -> bool:
    """A stored memory is written as 'User: {msg}\\nAI: {reply}'. It is redundant
    only if EACH of its halves near-matches (>= _MEMORY_REDUNDANT_RATIO) some
    single recent history/summary line -- i.e. that exact turn is already visible
    and re-injecting it just duplicates context (RQ-02).

    Matching against discrete lines (not a substring of the concatenated blob)
    is deliberate: a short/common half like 'ok', or a distinct earlier turn
    whose text happens to be a substring of some unrelated later line, must NOT
    be dropped. Coupled to the storage format on purpose; if that changes this
    degrades to a harmless no-op. `recent_lines` are already _norm'd."""
    if not doc or not recent_lines:
        return False
    # maxsplit=1 on the first 'ai:' can mis-split a memory whose USER half itself
    # contains 'ai:'; that only ever weakens a half's match (-> memory kept), so
    # it can cause a missed drop but never a wrong drop.
    parts = re.split(r"\bai\s*:\s*", doc, maxsplit=1, flags=re.IGNORECASE)
    user_half = re.sub(r"^\s*user\s*:\s*", "", parts[0], flags=re.IGNORECASE)
    halves = [user_half] + (parts[1:] if len(parts) > 1 else [])
    normed = [_norm(h) for h in halves if _norm(h)]
    if not normed:
        return False

    def _present(half: str) -> bool:
        return any(
            SequenceMatcher(None, half, line).ratio() >= _MEMORY_REDUNDANT_RATIO
            for line in recent_lines
        )

    return all(_present(h) for h in normed)


# Role/boundary words that must never be forgeable from injected free text.
_ROLE_MARKERS = (
    "reply",
    "user",
    "assistant",
    "system",
    "you",
    "human",
    "ai",
    "char",
    "character",
)


class Brain:
    def __init__(self, vector_store: VectorStore, llm_client=None):
        self.vector_store = vector_store
        self.llm = llm_client or vector_store.llm_client
        self.budget_calc = ContextBudgetCalculator(llama_url=self.llm.url)

    @staticmethod
    def _sanitize(text: Any, extra_names=()) -> str:
        """Neutralize role/boundary markers in free-text card/persona fields so a
        crafted value can't forge fake dialogue turns or a premature 'Reply:'
        cutoff. Collapses newlines (no injected line can start a new role) and
        strips the colon after any role keyword (incl. the live user/char name)."""
        if not text:
            return ""
        text = re.sub(r"[\r\n]+", " ", str(text))
        markers = list(_ROLE_MARKERS) + [str(n).lower() for n in extra_names if n]
        pattern = r"(?i)\b(" + "|".join(re.escape(m) for m in markers) + r")\s*:"
        text = re.sub(pattern, lambda m: m.group(1) + " ", text)
        return text.strip()

    @staticmethod
    def _truncate_tokens(text: Any, max_tokens: int, from_end: bool = False) -> str:
        """Hard-cap a layer to ~max_tokens (1 tok ~ 4 chars) so an oversized
        field can't blow past context_size and push the master prompt off the
        top of the window. `from_end=True` keeps the TAIL (most recent) instead
        of the head -- used for the rolling summary, whose newest lines matter
        most (RF-05)."""
        if not text:
            return ""
        text = str(text)
        max_chars = max(0, int(max_tokens) * 4)
        if len(text) <= max_chars:
            return text
        if from_end:
            return "[…] " + text[-max_chars:].lstrip()
        return text[:max_chars].rstrip() + " […]"

    async def build_prompt(
        self,
        user_message: str,
        character: Any,
        state: Dict[str, Any],
        user: Any = None,
        history: List[Any] = None,
        db: Session = None,
        chat_id: Any = None,
        interaction_count: int = 0,
        lore_cooldowns: Dict[str, Any] = None,
    ) -> str:
        """Assembles the ultra-compact 6-layer prompt for models 1-4B using Token Budgeting."""
        budget = await self.budget_calc.get_budget()

        # Layer 1: Memories (RAG). Scope to (character, chat) so one chat/session
        # never retrieves another's memories. Legacy memories with no chat_id
        # simply won't match the exact-match filter -> no cross-chat poison.
        memory_filter = None
        if character:
            memory_filter = {"character_id": character.id}
            if chat_id is not None:
                memory_filter["chat_id"] = chat_id
        context_data = await self.vector_store.query_memory(
            user_message,
            metadata_filter=memory_filter,
        )
        # Raw docs captured here; the injectable string is assembled below once
        # _names is known, so memories get the same sanitize+cap as every other
        # free-text layer (PZ-05).
        memory_docs = []
        if isinstance(context_data, dict) and context_data.get("documents"):
            memory_docs = context_data["documents"][0] or []

        allocations = budget.get("allocations", {})

        # Layer 1.5: Lorebooks (Keyword-triggered via Regex Scanner V2)
        lore_context = ""
        if db and character:
            from src.backend.core.context.lorebook_scanner import LorebookScanner

            scanner = LorebookScanner(db)
            hist_texts = [
                (
                    m.get("content")
                    if isinstance(m, dict)
                    else getattr(m, "content", "")
                )
                or ""
                for m in (history or [])
            ]
            active_lore = scanner.scan_and_extract(
                user_message,
                character.id,
                history=hist_texts,
                turn_index=interaction_count,
                cooldowns=lore_cooldowns,
            )
            if active_lore:
                lore_text = "\n".join([f"- {self._sanitize(d)}" for d in active_lore])
                lore_text = self._truncate_tokens(
                    lore_text, allocations.get("lorebook_cap", 500)
                )
                lore_context = "\nLore:\n" + lore_text

        # Layer 1.5: Summary (raw here; sanitized + assembled below once _names
        # is known, so the LLM-generated summary can't forge role markers, PZ-06).
        raw_summary = state.get("active_summary", "") if state else ""

        # Layer 2: History (Dynamic Sliding Window)
        user_name = user.name if user else "User"
        char_name = character.name if character else "You"

        history_lines = []
        if history:
            for msg in history:
                role_val = (
                    msg["role"] if isinstance(msg, dict) else getattr(msg, "role", "")
                )
                role = user_name if role_val == "user" else char_name
                content = (
                    msg.content if hasattr(msg, "content") else msg.get("content", "")
                )
                history_lines.append(f"{role}: {content}")

        # Enforce budget for history
        history_str = ""
        if history_lines:
            history_budget = budget.get("history_budget", 2048)  # Default fallback
            current_tokens = 0
            allowed_lines = []

            # Start from the most recent (end of list) and go backwards
            for idx, line in enumerate(reversed(history_lines)):
                # Approximation for speed: 1 token ~ 4 chars
                est_tokens = len(line) // 4 + 5
                if current_tokens + est_tokens <= history_budget:
                    allowed_lines.insert(0, line)
                    current_tokens += est_tokens
                elif idx == 0:
                    # The most recent turn is the single most important line for
                    # continuity -- never drop it wholesale. Hard-truncate its
                    # head to fit (small floor so a tiny budget still yields a
                    # usable fragment), keeping the leading role marker.
                    keep_chars = max(history_budget * 4, 240)
                    allowed_lines.insert(0, line[:keep_chars])
                    break
                else:
                    break
            history_str = "\n".join(allowed_lines)

        # Layer 3: Identity & Tags & Persona.
        # All free-text card/persona fields are sanitized so a crafted value
        # cannot forge role markers ("User:", "Reply:", char/user name + ":").
        char_display_name = character.nickname if (character and getattr(character, "nickname", None)) else (character.name if character else "You")
        _names = (user_name, char_name, char_display_name)

        # Layer 1 (assembled now that _names is known): retrieved memories are
        # sanitized -- a stored memory can contain "User:"/"Reply:" markers +
        # newlines and would otherwise forge dialogue turns -- and length-capped
        # so they can't overflow the context window (PZ-05).
        context = "None."
        if memory_docs:
            # Drop memories that just replay a turn already visible in the recent
            # history/summary -- injecting them again duplicates context and
            # over-weights that moment (RQ-02). Compare against discrete lines so
            # a distinct memory isn't dropped for coincidentally overlapping
            # unrelated text.
            recent_lines = [
                _norm(
                    (
                        m.get("content")
                        if isinstance(m, dict)
                        else getattr(m, "content", "")
                    )
                    or ""
                )
                for m in (history or [])
            ]
            recent_lines += [_norm(ln) for ln in (raw_summary or "").splitlines()]
            recent_lines = [ln for ln in recent_lines if ln]
            fresh_docs = [
                d
                for d in memory_docs
                if d and not _memory_redundant_with_recent(str(d), recent_lines)
            ]
            sanitized = [self._sanitize(str(d), _names) for d in fresh_docs if d]
            joined = " ".join(s for s in sanitized if s)
            if joined:
                context = self._truncate_tokens(joined, allocations.get("memory", 400))

        summary_context = ""
        if raw_summary:
            clean_summary = self._truncate_tokens(
                self._sanitize(raw_summary, _names),
                allocations.get("chat_summary", 200),
                from_end=True,
            )
            if clean_summary:
                summary_context = f"\nSummary:\n{clean_summary}\n"
        # Cap each free-text card field so one pathologically long field can't
        # blow past context_size and push history/master prompt off the top
        # (PB-01). Each is bounded by the character_def allocation.
        _card_cap = allocations.get("character_def", 300)
        short_desc = getattr(character, "short_description", None) or getattr(character, "description", None) or ""
        short_desc = self._truncate_tokens(
            self._sanitize(render_macros(short_desc, char_name, user_name), _names),
            _card_cap,
        )
        identity = (
            f"{char_display_name}. {short_desc}"
            if character
            else "You are unique."
        )

        persona_str = ""
        if character and getattr(character, "persona_prompt", None):
            persona = self._truncate_tokens(
                self._sanitize(render_macros(character.persona_prompt, char_name, user_name), _names),
                _card_cap,
            )
            persona_str = f"Personality: {persona}\n"

        scenario_str = ""
        if character and getattr(character, "scenario", None):
            scenario = self._truncate_tokens(
                self._sanitize(render_macros(character.scenario, char_name, user_name), _names),
                _card_cap,
            )
            scenario_str = f"Scenario: {scenario}\n"

        example_dialogs_str = ""
        if character and getattr(character, "mes_example", None):
            # mes_example is few-shot dialogue: its role labels ("{{char}}:",
            # "{{user}}:") are the intended format, and it's authored at the same
            # trust level as the rest of the card -- so resolve macros and cap
            # its length, but do NOT sanitize role markers out of it.
            example = self._truncate_tokens(
                render_macros(character.mes_example, char_name, user_name),
                allocations.get("mes_example", 300),
            )
            example_dialogs_str = f"Example Dialogs:\n{example}\n\n"

        tags = []
        if character and character.tags:
            for t in character.tags:
                tags.append(
                    f"[{self._sanitize(t.label, _names)}]: {self._sanitize(t.instruction, _names)}"
                )

        user_persona = ""
        if user:
            persona_parts = []
            if user.gender and user.gender != "Unknown":
                persona_parts.append(f"Gender: {self._sanitize(user.gender, _names)}")
            if getattr(user, "appearance", None):
                persona_parts.append(f"Appearance: {self._sanitize(user.appearance, _names)}")
            if getattr(user, "persona_description", None):
                persona_parts.append(f"Persona: {self._sanitize(user.persona_description, _names)}")
            if persona_parts:
                user_persona = self._truncate_tokens(
                    f"User ({user_name}): " + " | ".join(persona_parts),
                    allocations.get("user_persona", 100),
                )

        # Layer 4: State (Compressed)
        state_str = compress_state(state, user_name)

        # Format via LangChain PromptTemplate
        return ENTITY_PROMPT_TEMPLATE.format(
            master_prompt=COMPRESSED_MASTER_PROMPT,
            identity=identity,
            persona_str=persona_str,
            scenario_str=scenario_str,
            example_dialogs_str=example_dialogs_str,
            modifiers="\n".join(tags),
            user_persona=user_persona,
            state_str=state_str,
            context=context,
            lore_context=lore_context,
            summary_context=summary_context,
            history_str=history_str,
            user_info=user_name,
            user_message=user_message,
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
            role = (
                msg["role"].capitalize()
                if isinstance(msg, dict)
                else getattr(msg, "role", "").capitalize()
            )
            content = (
                msg["content"] if isinstance(msg, dict) else getattr(msg, "content", "")
            )
            prompt += f"{role}: {content}\n"

        result = await self.llm.complete(prompt, grammar=REFLECTION_GRAMMAR)
        return self._safe_json_parse(result.get("content", "{}"))

    async def suggest_tags(self, description: str, db: Session) -> List[int]:
        """Suggests appropriate personality tag IDs based on description."""
        all_tags = db.query(Tag).all()
        if not all_tags:
            return []

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
