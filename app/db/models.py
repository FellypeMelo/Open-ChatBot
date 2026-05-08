from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

# Junction table for Character <-> Tag (Many-to-Many)
character_tags = Table(
    "character_tags",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, unique=True, index=True)
    instruction = Column(Text) # The prompt snippet this tag injects

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    persona_prompt = Column(Text)
    is_active = Column(Boolean, default=True)

    # Relationships
    tags = relationship("Tag", secondary=character_tags, backref="characters")
    state = relationship("AgentState", back_populates="character", uselist=False, cascade="all, delete-orphan")

class AgentState(Base):
    __tablename__ = "agent_states"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), unique=True)
    location = Column(String, default="Living Room")
    mood = Column(String, default="Neutral")
    clothes = Column(String, default="Casual")
    
    # Needs, Relationships, etc.
    stats = Column(JSON)

    character = relationship("Character", back_populates="state")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.stats:
            self.stats = {
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
