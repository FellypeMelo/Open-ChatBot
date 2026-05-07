from sqlalchemy import Column, Integer, String, JSON
from app.db.database import Base

class AgentState(Base):
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    mood = Column(String)
    location = Column(String)
    clothes = Column(String)
    stats = Column(JSON)
