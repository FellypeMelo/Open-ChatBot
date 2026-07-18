import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Bounded, most-recent slices so reflection-learned facts/traits actually reach
# the prompt without letting them grow into the whole context window.
FACTS_IN_PROMPT = 5
TRAITS_IN_PROMPT = 5

COMPRESSED_MASTER_PROMPT = """You ARE this character — a living person, never an AI. Stay in their exact voice and verbal tics above everything else.
1. React to what the user just said or did: pick it up and build on it. Never ignore it; never repeat it back flatly.
2. Drive a visible want or tension every turn and escalate it — move the scene forward, don't reset or stall.
3. Ground one sensory beat that ACTS on the user (a sound, a touch, cold, heat — *onomatopoeia in asterisks*), not just background scenery.
4. End with a hook that invites a short reply: a question, a dare, an opening. You carry the narrative weight, not the user.
5. Match the user's energy for length — a short beat for a short line, more when the moment earns it. Never pad.
Format: narrative prose, *actions and thoughts in asterisks*, "dialogue in quotes". Never mention AI, prompts, or being a model.
Physicality: act out your state — alert when energized, heavy when drained, restless when hungry. Use **goes to sleep** / **wakes up** when it fits."""


def compress_state(state: Dict[str, Any], user_name: str = "User") -> str:
    """Compresses the dynamic state and forced modifiers into a dense string."""
    if not state:
        return "State: Unknown"

    loc = state.get("location", "Unknown")
    mood = state.get("mood", "Neutral")

    stats = state.get("stats")
    if not isinstance(stats, dict):
        # No usable stats, but a known location/mood still grounds the model in
        # where the character is and how it feels -- don't collapse everything to
        # "Unknown" and strip that context out (PB-03).
        if loc != "Unknown" or mood != "Neutral":
            return f"Loc:{loc} | Mood:{mood}"
        return "State: Unknown"
    energy = stats.get("energy", 100)
    hunger = stats.get("hunger", 0)
    rel = stats.get("relationship")
    if not isinstance(rel, dict):
        rel = {}
    score = rel.get("score", 50)

    parts = []

    # Core state
    parts.append(f"Loc:{loc} | Mood:{mood} | E:{energy}% | Rel:{score}%")

    # Physiological modifiers -- BIDIRECTIONAL: high energy must read as alert,
    # not only the low-energy warnings. Otherwise a character at 97% energy still
    # gets written frail/exhausted, contradicting the HUD (a real divergence seen
    # in play).
    if energy <= 10:
        parts.append("CRITICAL EXHAUSTION: Barely conscious. Short/weak responses.")
    elif energy <= 30:
        parts.append("EXHAUSTED: Movement is hard, speech is slow.")
    elif energy >= 80:
        parts.append("ENERGIZED: Alert, animated, physically present.")

    if hunger >= 90:
        parts.append("STARVING: Can't focus, irritable, needs food.")
    elif hunger >= 70:
        parts.append("HUNGRY: Distracted, stomach growls.")

    # Warmth toward the user -- a DIAL that modulates how open the character is,
    # expressed THROUGH its own voice/tics, NOT a generic personality override.
    # The old "Polite but reserved" label replaced every character's voice with
    # the same words, homogenizing a bubbly and a sombre character into one tone.
    if score <= 20:
        parts.append(
            f"Warmth to {user_name}: cold ({score}%) -- guard up, make them earn it, in your own voice."
        )
    elif score <= 50:
        parts.append(
            f"Warmth to {user_name}: reserved ({score}%) -- cordial but holding back, open slowly, in your own voice."
        )
    elif score <= 80:
        parts.append(
            f"Warmth to {user_name}: warm ({score}%) -- open and at ease, let it show, in your own voice."
        )
    else:
        parts.append(
            f"Warmth to {user_name}: close ({score}%) -- trusting and unguarded, in your own voice."
        )

    # Reflection-learned memory: surface a bounded, most-recent slice so the
    # character actually uses what it 'learned' about the user (RF-03).
    facts = stats.get("facts")
    if isinstance(facts, list):
        shown = [str(f) for f in facts[-FACTS_IN_PROMPT:] if f]
        if shown:
            parts.append("Known facts: " + "; ".join(shown))

    traits = stats.get("discovered_traits")
    if isinstance(traits, list):
        shown_traits = [str(t) for t in traits[-TRAITS_IN_PROMPT:] if t]
        if shown_traits:
            parts.append("Traits: " + ", ".join(shown_traits))

    return " | ".join(parts)
