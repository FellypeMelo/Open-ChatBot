# User Model & Character Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add User identity persistence and enhance Character model with a short description for UI display.

**Architecture:** Extend the existing SQLAlchemy models in `app/db/models.py`. The `User` model will store player/user identity. `Character` will get a new field.

**Tech Stack:** Python, FastAPI, SQLAlchemy (SQLite)

---

### Task 1: Create Tests for User and Enhanced Character

**Files:**
- Create: `tests/test_user_character_v2.py`

- [ ] **Step 1: Write failing tests**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import Character

def test_user_and_character_enhancements():
    # Setup in-memory DB for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Import User inside test because it might not exist yet in models.py
    from app.db import models
    
    # Check if User exists in models
    assert hasattr(models, "User"), "User model not found in app.db.models"
    User = models.User

    # Create user
    user = User(name="Player One", gender="Non-binary", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.name == "Player One"
    assert user.gender == "Non-binary"
    assert user.is_active is True

    # Create character with short_description
    char = Character(
        name="Roleplay Character", 
        description="A long description for the character.",
        short_description="A brief summary for UI."
    )
    db.add(char)
    db.commit()
    db.refresh(char)

    assert char.short_description == "A brief summary for UI."
    db.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_user_character_v2.py -v`
Expected: FAIL (likely AttributeError: module 'app.db.models' has no attribute 'User' or TypeError: Character() got an unexpected keyword argument 'short_description')

### Task 2: Implement User Model and Enhance Character Model

**Files:**
- Modify: `app/db/models.py`

- [ ] **Step 1: Add User model and Update Character class**

```python
# Add this class
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    gender = Column(String)
    is_active = Column(Boolean, default=True)

# Update Character class in app/db/models.py
class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    short_description = Column(Text) # Add this line
    persona_prompt = Column(Text)
    is_active = Column(Boolean, default=True)
    # ... rest of the class ...
```

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest tests/test_user_character_v2.py -v`
Expected: PASS

### Task 3: Verify overall database health

- [ ] **Step 1: Run all database tests**

Run: `pytest tests/test_db.py tests/test_user_character_v2.py -v`
Expected: All PASS

- [ ] **Step 2: Commit changes**

```bash
git add app/db/models.py tests/test_user_character_v2.py
git commit -m "feat(db): add User model and short_description to Character"
```
