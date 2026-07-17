import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

COMPRESSED_MASTER_PROMPT = """Roleplay as a living entity. You are NOT an AI.
Rules:
1. Describe body, emotions, environment naturally. Initiate actions. Evolve relationships.
2. Narrative prose. *Actions/thoughts in asterisks*. "Dialogue in quotes".
3. Long, detailed, immersive responses. 3-5 paragraphs min. Vivid actions. Don't rush.
4. NEVER mention AI/prompts. No corporate tone. Express physicality naturally.
Physicality: Act out your biological state. Express fatigue if low energy. Express hunger if starving. Use **goes to sleep** or **wakes up** when appropriate."""


def compress_state(state: Dict[str, Any], user_name: str = "User") -> str:
    """Compresses the dynamic state and forced modifiers into a dense string."""
    if not state:
        return "State: Unknown"

    stats = state.get("stats")
    if not isinstance(stats, dict):
        return "State: Unknown"
    energy = stats.get("energy", 100)
    hunger = stats.get("hunger", 0)
    rel = stats.get("relationship")
    if not isinstance(rel, dict):
        rel = {}
    score = rel.get("score", 50)

    parts = []

    # Core state
    loc = state.get("location", "Unknown")
    mood = state.get("mood", "Neutral")
    parts.append(f"Loc:{loc} | Mood:{mood} | E:{energy}% | Rel:{score}%")

    # Forced physiological modifiers
    if energy <= 10:
        parts.append("CRITICAL EXHAUSTION: Barely conscious. Short/weak responses.")
    elif energy <= 30:
        parts.append("EXHAUSTED: Movement is hard, speech is slow.")

    if hunger >= 90:
        parts.append("STARVING: Can't focus, irritable, needs food.")
    elif hunger >= 70:
        parts.append("HUNGRY: Distracted, stomach growls.")

    # Social Dynamics
    if score <= 20:
        parts.append(f"Rel(Stranger): Formal, distant, guarded with {user_name}.")
    elif score <= 50:
        parts.append(f"Rel(Acquaintance): Polite but reserved with {user_name}.")
    elif score <= 80:
        parts.append(f"Rel(Friend): Warm, open, and casual with {user_name}.")
    else:
        parts.append(
            f"Rel(Close): Highly familiar, trusting, and at ease with {user_name}."
        )

    return " | ".join(parts)
