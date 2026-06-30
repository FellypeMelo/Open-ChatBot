from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey, Table, DateTime, Float
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
    
    persona_description = Column(Text, default="")
    appearance = Column(Text, default="")

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
    interaction_count = Column(Integer, default=0)
    location = Column(String, default="Living Room")
    mood = Column(String, default="Neutral")
    clothes = Column(String, default="Casual")
    
    # Needs, Relationships, etc.
    stats = Column(JSON)
    
    # Active summary of past interactions
    active_summary = Column(Text, default="")

    character = relationship("Character", back_populates="state")
    current_message = relationship("MessageNode", foreign_keys=[current_message_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.location is None: self.location = "Living Room"
        if self.clothes is None: self.clothes = "Casual"
        if self.mood is None: self.mood = "Neutral"
        if self.interaction_count is None: self.interaction_count = 0
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
    request_id = Column(String, index=True, nullable=True)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    children = relationship("MessageNode", backref=backref("parent", remote_side=[id]))
    character = relationship("Character")
    user = relationship("User")

class LorebookEntry(Base):
    __tablename__ = "lorebook_entries"
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True) # Used as title/name
    keys = Column(JSON, default=list) # Primary keys/regexes for matching
    secondary_keys = Column(JSON, default=list)
    content = Column(Text)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True, index=True)
    is_global = Column(Boolean, default=False)
    
    insertion_order = Column(Integer, default=100)
    probability = Column(Integer, default=100)
    scan_depth = Column(Integer, default=5)
    is_constant = Column(Boolean, default=False)
    cooldown_turns = Column(Integer, default=0)

    character = relationship("Character")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    content = Column(Text)
    summary = Column(Text)
    mood_at_time = Column(String)
    relationship_score = Column(Integer)
    energy_level = Column(Integer)

    character = relationship("Character")

class SamplerPreset(Base):
    __tablename__ = "sampler_presets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_default = Column(Boolean, default=False)
    
    # Standard samplers
    temperature = Column(Float, default=1.0)
    min_p = Column(Float, default=0.05)
    top_k = Column(Integer, default=0)
    top_p = Column(Float, default=1.0)
    repeat_penalty = Column(Float, default=1.0)
    
    # DRY (Don't Repeat Yourself)
    dry_multiplier = Column(Float, default=0.0)
    dry_base = Column(Float, default=1.75)
    dry_range = Column(Integer, default=2048)
    
    # XTC (Exclude Top Choice)
    xtc_threshold = Column(Float, default=0.0)
    xtc_probability = Column(Float, default=0.0)
