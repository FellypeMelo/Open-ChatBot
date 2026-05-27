from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, backref
from src.backend.db.database import Base
from datetime import datetime, timezone

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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    gender = Column(String)
    is_active = Column(Boolean, default=True)

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    short_description = Column(Text)
    persona_prompt = Column(Text)
    is_active = Column(Boolean, default=True)

    # Relationships
    tags = relationship("Tag", secondary=character_tags, backref="characters")
    state = relationship("AgentState", back_populates="character", uselist=False, cascade="all, delete-orphan")

    @classmethod
    def get_default(cls, db):
        return db.query(cls).first() or cls(name="Gemi", description="Playful entity.")

class AgentState(Base):
    __tablename__ = "agent_states"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), unique=True, index=True)
    current_message_id = Column(Integer, ForeignKey("message_nodes.id"), nullable=True)
    location = Column(String, default="Living Room")
    mood = Column(String, default="Neutral")
    clothes = Column(String, default="Casual")
    
    # Needs, Relationships, etc.
    stats = Column(JSON)

    character = relationship("Character", back_populates="state")
    current_message = relationship("MessageNode", foreign_keys=[current_message_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.stats:
            self.stats = {
                "energy": 100,
                "hunger": 0,
                "happiness": 100,
                "social": 100,
                "is_sleeping": False,
                "last_update": datetime.now(timezone.utc).isoformat(),
                "relationship": {
                    "score": 50,
                    "dynamic_preferences": ["teasing", "playful"],
                    "user_sentiment": "Neutral"
                }
            }

class MessageNode(Base):
    __tablename__ = "message_nodes"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("message_nodes.id"), nullable=True)
    role = Column(String) # 'user' or 'assistant'
    content = Column(Text) # Raw message or sequence JSON
    type = Column(String, default="speech") # 'thought', 'action', 'speech'
    variant_index = Column(Integer, default=0)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    children = relationship("MessageNode", backref=backref("parent", remote_side=[id]))
    character = relationship("Character")
    user = relationship("User")

class LorebookEntry(Base):
    __tablename__ = "lorebook_entries"
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    content = Column(Text)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True, index=True)
    is_global = Column(Boolean, default=False)

    character = relationship("Character")
