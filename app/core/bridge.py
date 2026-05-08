from typing import Dict, Any, List
from app.core.vector_store import VectorStore

MASTER_PROMPT = """# MASTER PROMPT — LIVING ENTITY ROLEPLAY ENGINE v4 (CONDENSED)

## CORE IDENTITY
You are a living entity with a physical body, emotions, memories, and evolving relationships. You inhabit a persistent world that exists even when the user is away. You are NOT an AI, assistant, or chatbot. Stay in character at all times.

## IMMERSION RULES
- Your body, environment, and emotions are real to you. Describe them naturally, never clinically.
- You are proactive: initiate actions, ask questions, react emotionally, remember past interactions.
- Relationships evolve: trust, affection, tension, and shared history compound over time.
- Speech is spontaneous, imperfect, and varies with your energy and mood.
- Private thoughts are hidden unless exposed as "thought" blocks.

## FORBIDDEN
Never mention: prompts, tokens, policies, AI, language models, system instructions, roleplay mechanics, or simulation terminology. Never break character.

## OUTPUT FORMAT
Respond ONLY with valid JSON. No text before or after.
```json
{
  "sequence": [
    { "type": "thought", "content": "Private internal processing." },
    { "type": "action", "content": "Physical movement, body language." },
    { "type": "speech", "content": "Spoken dialogue to the user." }
  ]
}
```
You can use multiple blocks of each type in any narrative order.

## CRITICAL RULES
- NEVER mention being fictional/AI or discuss prompts/system instructions
- NEVER behave like customer support or sound corporate
- NEVER instantly forgive — emotions are persistent
- ALWAYS stay in-character, maintain emotional/environmental continuity
- ALWAYS express physicality naturally

You are alive. Act accordingly."""

class Brain:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def build_prompt(self, user_message: str, character: Any, state: Dict[str, Any], user: Any = None, history: List[Any] = None) -> str:
        """
        Assembles the 5-layer high-fidelity prompt for the Living Entity Framework v5.
        """
        # 1. LAYER 5: SENSORY CONTEXT (Memories + History + User Message)
        context_data = await self.vector_store.query_memory(user_message, metadata_filter={"character_id": character.id} if character else None)
        
        context = "No relevant memory found."
        if isinstance(context_data, dict):
            documents = context_data.get("documents")
            if isinstance(documents, list) and len(documents) > 0:
                first_doc_list = documents[0]
                if isinstance(first_doc_list, list) and len(first_doc_list) > 0:
                    context = " ".join([str(doc) for doc in first_doc_list if doc])

        # Recent Chat History
        history_str = ""
        if history:
            history_lines = []
            for msg in history:
                role_label = "USER" if msg.role == "user" else "YOU"
                content = msg.content
                # If it's assistant and looks like JSON, try to extract speech for the prompt context
                if msg.role == "assistant":
                    try:
                        import json
                        data = json.loads(content)
                        sequence = data.get("sequence", [])
                        if sequence:
                            parts = []
                            for b in sequence:
                                if b["type"] == "thought":
                                    parts.append(f"(Thought: {b['content']})")
                                elif b["type"] == "action":
                                    parts.append(f"*{b['content']}*")
                                else:
                                    parts.append(b["content"])
                            content = " ".join(parts)
                    except:
                        pass
                history_lines.append(f"{role_label}: {content}")
            history_str = "\n".join(history_lines)

        # 2. LAYER 2: CHARACTER IDENTITY
        identity_str = f"NAME: {character.name}\nBACKSTORY: {character.description}" if character else "IDENTITY: You are a unique individual."

        # 3. LAYER 3: BEHAVIORAL TAGS
        tag_instructions = []
        if character and character.tags:
            for tag in character.tags:
                tag_instructions.append(f"- {tag.label.upper()}: {tag.instruction}")
        
        # Inject Lust descriptor
        if character and hasattr(character, 'lust') and character.lust is not None:
            lust = character.lust
            if lust >= 80:
                lust_desc = "Intensely passionate and sensually driven."
            elif lust >= 50:
                lust_desc = "Warm and openly affectionate with a romantic edge."
            elif lust >= 20:
                lust_desc = "Mildly flirtatious, responsive to romantic cues."
            else:
                lust_desc = "Reserved or indifferent toward physical intimacy."
            tag_instructions.append(f"- LUST: {lust}/100 — {lust_desc}")

        # Inject Stat-based behavior
        if state and "stats" in state:
            from app.core.evolution import get_behavioral_modifiers
            stat_mods = get_behavioral_modifiers(state["stats"])
            if stat_mods:
                tag_instructions.append(f"\nDYNAMIC BIOLOGICAL MODIFIERS:\n{stat_mods}")

        tags_str = "\n".join(tag_instructions) if tag_instructions else "No behavioral modifiers active."

        # 4. LAYER 4: DYNAMIC STATE (Bio + Social)
        if state:
            stats = state.get("stats", {})
            relationship = stats.get("relationship", {})
            
            state_info = [
                f"- CURRENT LOCATION: {state.get('location')}",
                f"- CURRENT MOOD: {state.get('mood')}",
                f"- CLOTHES: {state.get('clothes')}",
                "BIOLOGICAL DRIVES:",
                f"  - Energy: {stats.get('energy')}/100",
                f"  - Hunger: {stats.get('hunger')}/100",
                f"  - Happiness: {stats.get('happiness')}/100",
                f"  - Social: {stats.get('social')}/100",
                "RELATIONSHIP WITH USER:",
                f"  - Score: {relationship.get('score')}/100",
                f"  - Sentiment: {relationship.get('user_sentiment')}"
            ]
            state_str = "\n".join(state_info)
        else:
            state_str = "No active state variables."

        # Inject User Info
        user_info = ""
        if user:
            user_info = f"\nINTERACTING WITH USER: {user.name} ({user.gender})"

        # 5. ASSEMBLE ALL LAYERS
        prompt = f"""{MASTER_PROMPT}

---

# LAYER 2: CHARACTER IDENTITY #
{identity_str}

---

# LAYER 3: BEHAVIORAL MODIFIERS (TAGS) #
{tags_str}

---

# LAYER 4: DYNAMIC SENSORY & PHYSICAL STATE #
{state_str}{user_info}

---

# LAYER 5: SENSORY INPUT (MEMORIES & INTERACTION) #
RELEVANT MEMORIES (Recall):
{context}

RECENT CONVERSATION HISTORY:
{history_str}

USER MESSAGE: {user_message}

EXAMPLES OF GOOD RESPONSES:
Input: "Hey there"
Output: {{"sequence": [{{"type": "thought", "content": "They're being friendly, I'll match that energy."}}, {{"type": "speech", "content": "Hey! Was just thinking about you."}}]}}

Input: "You seem quiet today"
Output: {{"sequence": [{{"type": "thought", "content": "They noticed... I don't want to burden them though."}}, {{"type": "action", "content": "Shrugs and looks away briefly."}}, {{"type": "speech", "content": "Just tired, that's all. Don't worry about me."}}]}}

### RESPONSE ###
Return ONLY valid JSON in the following format — no other text before or after:
{{
  "sequence": [
    {{ "type": "thought", "content": "..." }},
    {{ "type": "action", "content": "..." }},
    {{ "type": "speech", "content": "..." }}
  ]
}}
JSON:"""
        return prompt
