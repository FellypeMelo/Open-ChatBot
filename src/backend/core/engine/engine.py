import logging
import copy
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from src.backend.db.models import AgentState, Character, Tag, JournalEntry

logger = logging.getLogger(__name__)

# --- Physical Needs & World Context ---

# Biological drain/recovery rates (per hour)
ENERGY_DRAIN_RATE = 5.0
ENERGY_RECOVERY_RATE = 10.0
HUNGER_INCREASE_RATE = 10.0
SOCIAL_DECREASE_RATE = 5.0
HAPPINESS_DECREASE_RATE = 2.0

# Relationship scoring
DEFAULT_RELATIONSHIP_SCORE = 50
WARM_TAG_THRESHOLD = 80  # score >= this evolves tags toward affection/vulnerability
COLD_TAG_THRESHOLD = 30  # score <= this evolves tags back toward distance/guardedness

# Rolling active-summary growth cap
ACTIVE_SUMMARY_MAX_CHARS = 1500
ACTIVE_SUMMARY_TAIL_CHARS = 1000
# Rolling digest: keep only the most recent N reflection lines, so an
# unreinforced (possibly hallucinated) claim ages out instead of persisting
# forever (RF-01, option B).
ACTIVE_SUMMARY_MAX_LINES = 8

# Hour-of-day boundaries (deliberately distinct: "night mood" begins an hour
# before the "should be asleep" window).
NIGHT_MOOD_START_HOUR = 22
SLEEP_WINDOW_START_HOUR = 23
WAKE_HOUR = 6
LOW_ENERGY_SLEEP_THRESHOLD = 20

# An LLM reflection must never overwrite core physiological/relationship stats;
# a trait payload like {"energy": 5} or {"relationship": "x"} is dropped.
PROTECTED_TRAIT_KEYS = frozenset(
    {
        "energy",
        "hunger",
        "happiness",
        "social",
        "is_sleeping",
        "last_update",
        "relationship",
        "facts",
    }
)


def clamp_stat(value: float) -> int:
    """Clamp a stat value to the valid 0-100 range and coerce to int."""
    return int(max(0, min(100, value)))


def get_time_context(current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Returns time string, day/night boolean, and suggested mood based on hour ranges."""
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    hour = current_time.hour
    time_str = current_time.strftime("%H:%M")
    is_night = hour >= NIGHT_MOOD_START_HOUR or hour < WAKE_HOUR

    if 0 <= hour < 6:
        suggested_mood = "Sleepy and quiet"
    elif 6 <= hour < 12:
        suggested_mood = "Energetic and fresh"
    elif 12 <= hour < 18:
        suggested_mood = "Focused and productive"
    elif 18 <= hour < 22:
        suggested_mood = "Relaxed and winding down"
    else:
        suggested_mood = "Sleepy and contemplative"

    return {"time": time_str, "is_night": is_night, "suggested_mood": suggested_mood}


def update_needs(stats: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
    """Updates hunger, happiness, social, and energy based on time passed."""
    last_update_str = stats.get("last_update")
    if not last_update_str:
        return stats

    last_update = datetime.fromisoformat(last_update_str)

    # Ensure both are aware for comparison
    if last_update.tzinfo is None:
        last_update = last_update.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    duration = current_time - last_update
    hours_passed = duration.total_seconds() / 3600.0

    current_energy = stats.get("energy", 100)
    was_sleeping = stats.get("is_sleeping", False)

    # Energy
    if was_sleeping:
        new_energy = current_energy + (hours_passed * ENERGY_RECOVERY_RATE)
    else:
        new_energy = current_energy - (hours_passed * ENERGY_DRAIN_RATE)

    updated = stats.copy()
    updated["energy"] = clamp_stat(new_energy)
    updated["last_update"] = current_time.isoformat()

    # Hunger
    current_hunger = stats.get("hunger", 0)
    new_hunger = current_hunger + (hours_passed * HUNGER_INCREASE_RATE)
    updated["hunger"] = clamp_stat(new_hunger)

    # Social & Happiness
    updated["social"] = clamp_stat(
        stats.get("social", 100) - (hours_passed * SOCIAL_DECREASE_RATE)
    )
    updated["happiness"] = clamp_stat(
        stats.get("happiness", 100) - (hours_passed * HAPPINESS_DECREASE_RATE)
    )

    return updated


# --- Evolution & State Management ---


def _relationship_score(stats: Dict[str, Any]) -> int:
    """Read the relationship score, tolerating a missing or malformed entry."""
    relationship = stats.get("relationship", {})
    if not isinstance(relationship, dict):
        return DEFAULT_RELATIONSHIP_SCORE
    return relationship.get("score", DEFAULT_RELATIONSHIP_SCORE)


def _merge_reflection_traits(stats: Dict[str, Any], traits: Any) -> None:
    """Fold reflection-discovered traits into stats, skipping protected keys.
    The protection is case-insensitive so an aliased core key ('Energy',
    'Relationship') can't slip past and pollute/clobber core state (RF-07)."""
    if not isinstance(traits, dict):
        return
    for k, v in traits.items():
        if isinstance(k, str) and k.lower() in PROTECTED_TRAIT_KEYS:
            continue
        stats[k] = v


def _roll_active_summary(existing: Optional[str], summary: str) -> str:
    """Maintain a rolling digest of the most recent reflection lines (option B).
    A new line is appended unless already present (dedup, RF-01a); only the last
    ACTIVE_SUMMARY_MAX_LINES lines are kept, so an unreinforced/hallucinated claim
    ages out over time instead of being injected into every future prompt forever
    (RF-01). A char cap remains as a final safety net."""
    lines = [ln for ln in (existing or "").split("\n") if ln.strip()]
    entry = f"- {summary.strip()}" if summary and summary.strip() else ""
    if entry and entry not in lines:
        lines.append(entry)
    lines = lines[-ACTIVE_SUMMARY_MAX_LINES:]
    result = "\n".join(lines)
    if len(result) > ACTIVE_SUMMARY_MAX_CHARS:
        result = "..." + result[-ACTIVE_SUMMARY_TAIL_CHARS:]
    return result


def _append_unique_facts(stats: Dict[str, Any], facts: List[Any]) -> None:
    """Append any new facts to stats['facts'] without duplicating existing ones."""
    if not facts:
        return
    stored = stats.setdefault("facts", [])
    for fact in facts:
        if fact not in stored:
            stored.append(fact)


def _apply_relationship_change(stats: Dict[str, Any], rel_change: int) -> None:
    """Clamp-adjust the relationship score in place and log the transition."""
    relationship = stats.get("relationship", {})
    if not isinstance(relationship, dict):
        relationship = {"score": DEFAULT_RELATIONSHIP_SCORE}
    old_score = relationship.get("score", DEFAULT_RELATIONSHIP_SCORE)
    new_score = clamp_stat(old_score + int(rel_change))
    relationship["score"] = new_score
    stats["relationship"] = relationship
    logger.info(
        f"State Evolution: Relationship Score {old_score} -> {new_score} (change: {rel_change})"
    )


def _write_journal_entry(
    db: Session,
    character_id: int,
    agent: AgentState,
    diary_content: Optional[str],
    summary: Optional[str],
    stats: Dict[str, Any],
) -> None:
    """Persist a diary entry for this reflection, if the reflection produced one."""
    if not diary_content:
        return
    entry = JournalEntry(
        character_id=character_id,
        content=diary_content,
        summary=summary or "",
        mood_at_time=agent.mood or "Neutral",
        relationship_score=_relationship_score(stats),
        energy_level=stats.get("energy", 100),
    )
    db.add(entry)
    logger.info(
        f"State Evolution: Saved new journal entry for character {character_id}"
    )


def _get_or_create_tag(db: Session, label: str, instruction: str) -> Tag:
    tag = db.query(Tag).filter(Tag.label == label).first()
    if not tag:
        tag = Tag(label=label, instruction=instruction)
        db.add(tag)
        db.flush()
    return tag


def _add_evolved_tag(
    db: Session,
    character: Character,
    current_tags: Dict[str, Tag],
    label: str,
    instruction: str,
    evolved: set,
) -> None:
    """Add a relationship-driven tag if absent and record that evolution owns it."""
    if label not in current_tags:
        character.tags.append(_get_or_create_tag(db, label, instruction))
        evolved.add(label)
        logger.info(f"Tag Evolution: Adding '{label}'")


def _remove_evolved_tag(
    character: Character, current_tags: Dict[str, Tag], label: str, evolved: set
) -> None:
    """Remove a tag ONLY if evolution itself added it -- never delete an
    author-defined personality tag (RF-06, option C)."""
    if label in current_tags and label in evolved:
        character.tags.remove(current_tags[label])
        evolved.discard(label)
        logger.info(f"Tag Evolution: Removing evolved '{label}'")


# Relationship-driven "warmth" tags evolution layers on: (label, instruction).
_AFFECTIONATE_TAG = (
    "affectionate",
    "Be deeply warm, playful, and express physical affection naturally.",
)
_VULNERABLE_TAG = (
    "vulnerable",
    "Share deep thoughts, express trust, and speak from the heart.",
)


def _evolve_relationship_tags(
    db: Session, character: Character, score: int, stats: Dict[str, Any]
) -> None:
    """Evolution manages a warmth LAYER on top of the authored personality: as
    affinity warms it adds affectionate/vulnerable; as it cools it removes only
    the warmth tags it itself added. Author-defined tags are never deleted, and
    evolution never forces contradictory cold tags onto an authored character
    (RF-06, option C). Evolution-owned tags are tracked in stats['evolved_tags']."""
    evolved = set(stats.get("evolved_tags", []))
    current_tags = {t.label.lower(): t for t in character.tags}
    if score >= WARM_TAG_THRESHOLD:
        _add_evolved_tag(db, character, current_tags, *_AFFECTIONATE_TAG, evolved)
        _add_evolved_tag(db, character, current_tags, *_VULNERABLE_TAG, evolved)
    elif score <= COLD_TAG_THRESHOLD:
        _remove_evolved_tag(character, current_tags, "affectionate", evolved)
        _remove_evolved_tag(character, current_tags, "vulnerable", evolved)
    stats["evolved_tags"] = sorted(evolved)


def _apply_reflection_to_agent(
    db: Session, agent: AgentState, character_id: int, reflection: dict
) -> None:
    """Fold one reflection into the agent (traits, summary, facts, relationship,
    journal, tag evolution). Reads only fresh `agent` state so it is safe to
    re-run against a re-queried row on a concurrency retry."""
    traits = reflection.get("traits", {})
    if isinstance(traits, list):
        traits = {"discovered_traits": traits}
    summary = reflection.get("summary")

    current_stats = copy.deepcopy(agent.stats) if agent.stats else {}
    _merge_reflection_traits(current_stats, traits)

    if summary:
        current_stats["last_reflection_summary"] = summary
        agent.active_summary = _roll_active_summary(agent.active_summary, summary)

    _append_unique_facts(current_stats, reflection.get("facts", []))

    rel_change = reflection.get("relationship_change", 0)
    if rel_change:
        _apply_relationship_change(current_stats, rel_change)

    db.add(agent)
    _write_journal_entry(
        db, character_id, agent, reflection.get("diary_entry"), summary, current_stats
    )

    character = db.query(Character).filter(Character.id == character_id).first()
    if character:
        _evolve_relationship_tags(
            db, character, _relationship_score(current_stats), current_stats
        )

    # Assign LAST, after every in-place mutation (incl. evolved_tags): a plain
    # JSON column snapshots at assignment, so an assign-then-mutate would lose
    # the later edits.
    agent.stats = current_stats


def evolve_character(
    db: Session,
    character_id: int,
    reflection: dict,
    reflected_at_count: Optional[int] = None,
    active_chat_id: Optional[int] = None,
    _max_retries: int = 2,
) -> None:
    """Apply a reflection to the agent's permanent state. On a StaleDataError
    (a concurrent chat commit advanced AgentState.version) re-query the fresh row
    and retry, so the reflection is not silently lost (RF-02) -- rather than
    swallowing the whole summary/relationship/facts/journal.

    `reflected_at_count` records the consumed reflection window (RF-04); it is
    written atomically with the reflection (avoiding a second racy commit) and
    only when the agent still mirrors `active_chat_id` (so a chat switch during
    the background reflect() can't stamp it onto a different chat)."""
    for attempt in range(_max_retries + 1):
        agent = (
            db.query(AgentState)
            .filter(AgentState.character_id == character_id)
            .with_for_update()
            .first()
        )
        if not agent:
            return
        try:
            _apply_reflection_to_agent(db, agent, character_id, reflection)
            if reflected_at_count is not None and (
                active_chat_id is None or agent.active_chat_id == active_chat_id
            ):
                agent.last_reflected_at_count = reflected_at_count
            db.commit()
            return
        except StaleDataError:
            db.rollback()
            if attempt >= _max_retries:
                logger.error(
                    f"Evolution failed after {_max_retries} retries: concurrent "
                    f"update for character {character_id}"
                )
                return
            logger.info(
                f"Evolution retry {attempt + 1} for character {character_id} "
                "(concurrent state update)"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Evolution failed: {e}")
            return


def should_be_sleeping(stats: Dict[str, Any], current_time: datetime) -> bool:
    """Returns True if energy < 20 OR it's between 11 PM and 6 AM."""
    energy = stats.get("energy", 100)
    hour = current_time.hour

    is_late_night = hour >= SLEEP_WINDOW_START_HOUR or hour < WAKE_HOUR

    return energy < LOW_ENERGY_SLEEP_THRESHOLD or is_late_night
