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
