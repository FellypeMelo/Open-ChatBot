from sqlalchemy import Column, Integer, String, JSON
from app.db.database import Base
from datetime import datetime

def get_default_stats():
    return {
        "energy": 100,
        "hunger": 0,
        "happiness": 100,
        "social": 100,
        "is_sleeping": False,
        "last_update": datetime.now().isoformat(),
        "relationship": {
            "score": 50,
            "dynamic_preferences": ["teasing", "playful"],
            "user_sentiment": "Neutral"
        }
    }

class AgentState(Base):
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    mood = Column(String)
    location = Column(String)
    clothes = Column(String)
    stats = Column(JSON, default=get_default_stats)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.stats is None:
            self.stats = get_default_stats()
