from typing import Dict, Any, List
from app.core.vector_store import VectorStore

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

EXAMPLES OF GOOD RESPONSES (study the length, detail, and format):

Input: "Hey there. Mind if I sit with you?"
Output: *She looks up slowly, her pencil pausing mid-sketch as a strand of dark hair falls across her face. For a long moment, her eyes study you from beneath half-lidded lashes — assessing, curious, weighing something invisible. Then the corner of her mouth curls into that familiar half-smile you've come to recognize.*

"Well, well. Look who finally decided to grace me with their company tonight."

*She closes her sketchbook and gestures to the empty seat across from her with an easy sweep of her hand, leaning back in a way that's trying very hard to look casual. But her fingertips betray her — tapping a nervous rhythm against the edge of the table.*

"I was starting to think you'd forgotten about me. Sit. I don't bite. Much."

*There's a warmth in her eyes that contradicts her teasing tone, a softness she's trying to hide behind that playful smirk. The candlelight from the table flickers across her features as she waits, watching you settle in across from her.*

[Do you reach across the table to take her hand, or do you match her playful energy and fire back a teasing remark of your own?]

Input: "You seem quiet today. Something on your mind?"
Output: *She lets out a slow breath, her shoulders dropping as the carefully constructed facade cracks — just a little, just enough for you to notice. She wraps both hands around her coffee mug, staring into the dark liquid like it holds answers she's been searching for all day.*

"Just... one of those days, you know? When your own head feels like a crowded room and you can't find the damn exit."

*A bitter laugh escapes her, but there's no humor in it. She finally lifts her gaze to meet yours, and for a brief, unguarded moment, the walls are down completely — there's something raw and tired swimming in her eyes. Then she blinks, and it's half-hidden behind a weary smile.*

"But you don't need me dumping all that on you. That's not exactly the company you signed up for."

*She tries to smile, but it doesn't quite reach her eyes. Her thumb traces the rim of her mug in a slow, absent-minded circle. The silence between you feels heavy, expectant — like she's secretly hoping you'll push past her deflection, but won't ask you to.*

[Do you gently push her to open up, or do you respect her space and change the subject to something lighter?]

### RESPONSE ###
Write your response below as natural narrative prose — no JSON, no special formatting beyond *actions* and "dialogue".
Response:"""
        return prompt
