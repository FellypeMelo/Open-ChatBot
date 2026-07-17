"""Narrative-action → agent-state transitions.

Pure domain logic for turning a character's narration (and quick-action
buttons) into concrete state changes: location/outfit moves, physiological
stat deltas, and gift/interaction stat modifiers. Kept out of the API layer so
the rules live in one place and are unit-testable without a request context.
"""

import logging
import re
from typing import Any, Dict, Optional

from src.backend.db.models import AgentState

logger = logging.getLogger(__name__)

_LEADING_ARTICLE = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)

# Quick-action buttons: the narration shown to the user plus the stat deltas
# applied server-side. The frontend only ever sees the message text.
ACTIONS_CONFIG = {
    "hug": {
        "message": "*I step forward and wrap my arms around you in a warm, gentle hug.*",
        "stats": {"happiness": 5, "social": 10, "relationship_score": 2},
    },
    "pat_head": {
        "message": "*I reach out and pat your head gently, smiling softly.*",
        "stats": {"happiness": 3, "social": 5, "relationship_score": 1},
    },
    "tease": {
        "message": "*I look at you with a playful smirk, teasing you lightly.*",
        "stats": {"happiness": 2, "social": 8, "relationship_score": 1},
    },
    "hold_hand": {
        "message": "*I slide my hand into yours, holding it gently.*",
        "stats": {"happiness": 4, "social": 8, "relationship_score": 2},
    },
    "coffee": {
        "message": "*I hand you a hot, freshly brewed cup of black coffee.*",
        "stats": {"hunger": -10, "energy": 15, "relationship_score": 2},
    },
    "croissant": {
        "message": "*I offer you a warm, freshly baked chocolate croissant.*",
        "stats": {"hunger": -35, "energy": 5, "relationship_score": 3},
    },
    "book": {
        "message": "*I present you with a beautifully bound, vintage book.*",
        "stats": {"happiness": 8, "social": 5, "relationship_score": 4},
    },
    "necklace": {
        "message": "*I hand you a small velvet box containing a delicate silver necklace.*",
        "stats": {"happiness": 15, "social": 10, "relationship_score": 8},
    },
}


def normalize_state_label(raw: str) -> str:
    """Clean a location/outfit label parsed from narration: trim, drop a leading
    article, and capitalize the first letter WITHOUT lowercasing the rest -- so a
    multi-word name like 'Grand Ballroom' is preserved, not mangled by
    str.capitalize() into 'Grand ballroom'."""
    label = _LEADING_ARTICLE.sub("", raw.strip().strip("."))
    return label[:1].upper() + label[1:]


def parse_actions_to_state(ai_response: str, state: AgentState) -> None:
    """Parse an AI reply for narrative actions like **enters [location]** and
    apply them to the live agent state (location, outfit, hunger, sleep)."""
    # Pattern for location: **enters [location]** or **walks into [location]**
    loc_match = re.search(
        r"\*\*(?:enters|walks into|arrives at|is now in) (.+?)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if loc_match:
        new_loc = normalize_state_label(loc_match.group(1))
        if new_loc != state.location:
            logger.info(f"State Update: Location -> {new_loc}")
            state.location = new_loc

    # Pattern for outfit: **changes into [outfit]** or **is wearing [outfit]**
    outfit_match = re.search(
        r"\*\*(?:changes into|puts on|is wearing|dresses in) (.+?)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if outfit_match:
        new_outfit = normalize_state_label(outfit_match.group(1))
        if new_outfit != state.clothes:
            logger.info(f"State Update: Clothes -> {new_outfit}")
            state.clothes = new_outfit

    # Physiological stats updates based on keywords in actions
    stats = dict(state.stats) if state.stats else {}

    # Check for eating/drinking
    eat_match = re.search(
        r"\*\*(?:eats|takes a bite of|chews on|drinks|sips|consumes|devours) (.+?)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if eat_match:
        old_hunger = stats.get("hunger", 0)
        new_hunger = max(0, old_hunger - 30)
        stats["hunger"] = new_hunger
        logger.info(
            f"State Update: Hunger {old_hunger}% -> {new_hunger}% due to eating action"
        )

    # Check for sleeping
    sleep_match = re.search(
        r"\*\*(?:goes to sleep|falls asleep|nods off|sleeps|rests her eyes)\*\*",
        ai_response,
        re.IGNORECASE,
    )
    if sleep_match:
        stats["is_sleeping"] = True
        logger.info("State Update: is_sleeping -> True due to sleeping action")

    # Check for waking up
    wake_match = re.search(
        r"\*\*(?:wakes up|stretches and yawns|wakes)\*\*", ai_response, re.IGNORECASE
    )
    if wake_match:
        stats["is_sleeping"] = False
        logger.info("State Update: is_sleeping -> False due to waking action")

    state.stats = stats


def apply_action_stats(
    stats: Optional[Dict[str, Any]], stat_mod: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply a quick-action's stat deltas to a stats dict, clamping every value
    to [0, 100] and defaulting a missing/malformed relationship to score 50."""
    stats = dict(stats) if stats else {}
    stats["energy"] = max(
        0, min(100, stats.get("energy", 100) + stat_mod.get("energy", 0))
    )
    stats["hunger"] = max(
        0, min(100, stats.get("hunger", 0) + stat_mod.get("hunger", 0))
    )
    stats["happiness"] = max(
        0, min(100, stats.get("happiness", 100) + stat_mod.get("happiness", 0))
    )
    stats["social"] = max(
        0, min(100, stats.get("social", 100) + stat_mod.get("social", 0))
    )

    relationship = stats.get("relationship", {})
    if not isinstance(relationship, dict):
        relationship = {"score": 50}
    old_score = relationship.get("score", 50)
    relationship["score"] = max(
        0, min(100, old_score + stat_mod.get("relationship_score", 0))
    )
    stats["relationship"] = relationship
    return stats
