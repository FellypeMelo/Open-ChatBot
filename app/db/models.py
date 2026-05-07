from sqlalchemy import Column, Integer, String, JSON
from app.db.database import Base

class AgentState(Base):
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    mood = Column(String)
    location = Column(String)
    clothes = Column(String)
    stats = Column(JSON, default={
        "energy": 100,
        "hunger": 0,
        "happiness": 100,
        "social": 100,
        "is_sleeping": False,
        "last_update": "2026-05-07T10:00:00"
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.stats is None:
            self.stats = {
                "energy": 100,
                "hunger": 0,
                "happiness": 100,
                "social": 100,
                "is_sleeping": False,
                "last_update": "2026-05-07T10:00:00"
            }
