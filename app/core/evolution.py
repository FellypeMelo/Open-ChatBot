import copy
from sqlalchemy.orm import Session
from app.db.models import AgentState

class EvolutionManager:
    def __init__(self, db: Session):
        self.db = db

    def evolve(self, agent_id: int, reflection: dict):
        """
        Apply reflections to the agent's permanent state.
        
        1. Fetch the AgentState.
        2. Deep-merge the traits from the reflection into the agent's stats.
        3. Commit the changes.
        """
        agent = self.db.query(AgentState).filter(AgentState.id == agent_id).first()
        if not agent:
            return

        traits = reflection.get("traits", {})
        summary = reflection.get("summary")
        facts = reflection.get("facts", [])
        
        try:
            # Ensure we have a deep copy to work with to trigger mutation detection
            current_stats = copy.deepcopy(agent.stats) if agent.stats else {}
                
            self._deep_merge(current_stats, traits)
            
            if summary:
                current_stats["last_reflection_summary"] = summary
                
            if facts:
                if "facts" not in current_stats:
                    current_stats["facts"] = []
                # Avoid duplicates when extending facts
                for fact in facts:
                    if fact not in current_stats["facts"]:
                        current_stats["facts"].append(fact)
            
            # Re-assign to trigger SQLAlchemy mutation detection
            agent.stats = current_stats
            
            self.db.add(agent)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def _deep_merge(self, base: dict, update: dict):
        """Recursively merge dictionaries and lists."""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_merge(base[key], value)
            elif isinstance(value, list) and key in base and isinstance(base[key], list):
                # Extend lists and remove duplicates
                for item in value:
                    if item not in base[key]:
                        base[key].append(item)
            else:
                base[key] = value

def get_behavioral_modifiers(stats: dict) -> str:
    mods = []
    
    # Energy (0-100):
    # < 20: "EXHAUSTED: You are barely able to speak. Short sentences, slurred words."
    # 20-50: "Tired, low initiative."
    energy = stats.get("energy", 100)
    if energy < 20:
        mods.append("EXHAUSTED: You are barely able to speak. Short sentences, slurred words.")
    elif energy <= 50:
        mods.append("Tired, low initiative.")
    
    # Hunger (0-100):
    # > 80: "STARVING: You are irritable, distracted by thoughts of food, and very impatient."
    hunger = stats.get("hunger", 0)
    if hunger > 80:
        mods.append("STARVING: You are irritable, distracted by thoughts of food, and very impatient.")
    
    # Relationship (0-100):
    # 0-20 (Stranger): "You are cold, distant, and formal. You don't trust the user."
    # 21-50 (Acquaintance): "You are polite but guarded. You keep things professional."
    # 51-80 (Friend): "You are warm, open, and enjoy their company. You can be more yourself."
    # 81-100 (Intimate): "You are deeply affectionate, playful, and vulnerable. You trust them completely."
    rel = stats.get("relationship", 0)
    if rel <= 20:
        mods.append("You are cold, distant, and formal. You don't trust the user.")
    elif rel <= 50:
        mods.append("You are polite but guarded. You keep things professional.")
    elif rel <= 80:
        mods.append("You are warm, open, and enjoy their company. You can be more yourself.")
    else:
        mods.append("You are deeply affectionate, playful, and vulnerable. You trust them completely.")
    
    return "\n".join(mods)
