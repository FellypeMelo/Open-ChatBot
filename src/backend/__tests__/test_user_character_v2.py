import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.db.database import Base
from src.backend.db.models import Character

def test_user_and_character_enhancements():
    # Setup in-memory DB for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Import User inside test because it might not exist yet in models.py
    from src.backend.db import models
    
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
