import logging
import copy
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from src.backend.db.models import AgentState

logger = logging.getLogger(__name__)

# --- Physical Needs & World Context ---

# Biological drain/recovery rates (per hour)
ENERGY_DRAIN_RATE = 5.0
ENERGY_RECOVERY_RATE = 10.0
HUNGER_INCREASE_RATE = 10.0
SOCIAL_DECREASE_RATE = 5.0
HAPPINESS_DECREASE_RATE = 2.0

def get_time_context(current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Returns time string, day/night boolean, and suggested mood based on hour ranges."""
    if current_time is None:
        current_time = datetime.now(timezone.utc)
        
    hour = current_time.hour
    time_str = current_time.strftime("%H:%M")
    is_night = hour >= 22 or hour < 6
    
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
        
    return {
        "time": time_str,
        "is_night": is_night,
        "suggested_mood": suggested_mood
    }

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
    updated["energy"] = int(max(0, min(100, new_energy)))
    updated["last_update"] = current_time.isoformat()

    # Hunger
    current_hunger = stats.get("hunger", 0)
    new_hunger = current_hunger + (hours_passed * HUNGER_INCREASE_RATE)
    updated["hunger"] = int(max(0, min(100, new_hunger)))
    
    # Social & Happiness
    updated["social"] = int(max(0, min(100, stats.get("social", 100) - (hours_passed * SOCIAL_DECREASE_RATE))))
    updated["happiness"] = int(max(0, min(100, stats.get("happiness", 100) - (hours_passed * HAPPINESS_DECREASE_RATE))))
    
    return updated

# --- Evolution & State Management ---

def evolve_character(db: Session, character_id: int, reflection: dict):
    """Apply reflections to the agent's permanent state with row-level locking."""
    # Use with_for_update to prevent race conditions during background evolution
    agent = db.query(AgentState).filter(AgentState.character_id == character_id).with_for_update().first()
    if not agent:
        return

    traits = reflection.get("traits", {})
    if isinstance(traits, list):
        traits = {"discovered_traits": traits}
        
    summary = reflection.get("summary")
    facts = reflection.get("facts", [])
    
    try:
        current_stats = copy.deepcopy(agent.stats) if agent.stats else {}
            
        if isinstance(traits, dict):
            current_stats.update(traits) # Simplified merge
        
        if summary:
            current_stats["last_reflection_summary"] = summary
            
        if facts:
            if "facts" not in current_stats:
                current_stats["facts"] = []
            for fact in facts:
                if fact not in current_stats["facts"]:
                    current_stats["facts"].append(fact)
        
        # Update relationship score dynamically
        rel_change = reflection.get("relationship_change", 0)
        if rel_change:
            relationship = current_stats.get("relationship", {})
            if not isinstance(relationship, dict):
                relationship = {"score": 50}
            old_score = relationship.get("score", 50)
            new_score = max(0, min(100, old_score + int(rel_change)))
            relationship["score"] = new_score
            current_stats["relationship"] = relationship
            logger.info(f"State Evolution: Relationship Score {old_score} -> {new_score} (change: {rel_change})")
        
        agent.stats = current_stats
        db.add(agent)

        # Save journal entry if present in reflection
        diary_content = reflection.get("diary_entry")
        if diary_content:
            from src.backend.db.models import JournalEntry
            relationship_info = current_stats.get("relationship", {})
            score = relationship_info.get("score", 50) if isinstance(relationship_info, dict) else 50
            
            entry = JournalEntry(
                character_id=character_id,
                content=diary_content,
                summary=summary or "",
                mood_at_time=agent.mood or "Neutral",
                relationship_score=score,
                energy_level=current_stats.get("energy", 100)
            )
            db.add(entry)
            logger.info(f"State Evolution: Saved new journal entry for character {character_id}")

        # Proposal 2: Dynamic Tag Evolution
        # Swap tags based on relationship score thresholds
        relationship_info = current_stats.get("relationship", {})
        score = relationship_info.get("score", 50) if isinstance(relationship_info, dict) else 50
        
        from src.backend.db.models import Character, Tag
        character = db.query(Character).filter(Character.id == character_id).first()
        if character:
            current_tags = {t.label.lower(): t for t in character.tags}
            
            # Helper to get or create a tag
            def get_or_create_tag(label: str, instruction: str) -> Tag:
                t = db.query(Tag).filter(Tag.label == label).first()
                if not t:
                    t = Tag(label=label, instruction=instruction)
                    db.add(t)
                    db.flush()
                return t

            # If relationship score >= 80, evolve guarded/distant tags into affectionate/vulnerable
            if score >= 80:
                # Swap "emotionally distant" -> "affectionate"
                if "emotionally distant" in current_tags:
                    character.tags.remove(current_tags["emotionally distant"])
                    logger.info("Tag Evolution: Removing 'emotionally distant'")
                if "affectionate" not in current_tags:
                    aff_tag = get_or_create_tag("affectionate", "Be deeply warm, playful, and express physical affection naturally.")
                    character.tags.append(aff_tag)
                    logger.info("Tag Evolution: Adding 'affectionate'")
                
                # Swap "guarded" -> "vulnerable"
                if "guarded" in current_tags:
                    character.tags.remove(current_tags["guarded"])
                    logger.info("Tag Evolution: Removing 'guarded'")
                if "vulnerable" not in current_tags:
                    vuln_tag = get_or_create_tag("vulnerable", "Share deep thoughts, express trust, and speak from the heart.")
                    character.tags.append(vuln_tag)
                    logger.info("Tag Evolution: Adding 'vulnerable'")
                    
            # If relationship score <= 30, swap warm tags back to guarded/distant
            elif score <= 30:
                # Swap "affectionate" -> "emotionally distant"
                if "affectionate" in current_tags:
                    character.tags.remove(current_tags["affectionate"])
                    logger.info("Tag Evolution: Removing 'affectionate'")
                if "emotionally distant" not in current_tags:
                    dist_tag = get_or_create_tag("emotionally distant", "Be cold, distant, and maintain strict personal boundaries.")
                    character.tags.append(dist_tag)
                    logger.info("Tag Evolution: Adding 'emotionally distant'")
                
                # Swap "vulnerable" -> "guarded"
                if "vulnerable" in current_tags:
                    character.tags.remove(current_tags["vulnerable"])
                    logger.info("Tag Evolution: Removing 'vulnerable'")
                if "guarded" not in current_tags:
                    guard_tag = get_or_create_tag("guarded", "Keep your guard up, avoid revealing personal details, and stay defensive.")
                    character.tags.append(guard_tag)
                    logger.info("Tag Evolution: Adding 'guarded'")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Evolution failed: {e}")

def get_behavioral_modifiers(stats: dict) -> str:
    """Converts numerical stats into prompt descriptors."""
    mods = []
    energy = stats.get("energy", 100)
    if energy < 20:
        mods.append("EXHAUSTED: You are barely able to speak. Short sentences, slurred words.")
    elif energy <= 50:
        mods.append("Tired, low initiative.")
    
    hunger = stats.get("hunger", 0)
    if hunger > 80:
        mods.append("STARVING: You are irritable, distracted by thoughts of food, and very impatient.")
    
    relationship = stats.get("relationship", {})
    rel_score = relationship.get("score", 50) if isinstance(relationship, dict) else 50
        
    if rel_score <= 20:
        mods.append("You are cold, distant, and formal. You don't trust the user.")
    elif rel_score <= 50:
        mods.append("You are polite but guarded. You keep things professional.")
    elif rel_score <= 80:
        mods.append("You are warm, open, and enjoy their company. You can be more yourself.")
    else:
        mods.append("You are deeply affectionate, playful, and vulnerable. You trust them completely.")
    
    return "\n".join(mods)

def should_be_sleeping(stats: Dict[str, Any], current_time: datetime) -> bool:
    """Returns True if energy < 20 OR it's between 11 PM and 6 AM."""
    energy = stats.get("energy", 100)
    hour = current_time.hour
    
    # Late night: 11 PM to 6 AM
    is_late_night = hour >= 23 or hour < 6
    
    return energy < 20 or is_late_night
