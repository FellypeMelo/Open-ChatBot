import pytest
from app.db.models import Character, Tag

def test_character_crud(client, db_session):
    # 1. Create
    response = client.post("/characters/", json={
        "name": "Luna",
        "description": "A mysterious space traveler."
    })
    assert response.status_code == 200
    data = response.json()
    char_id = data["id"]
    assert data["name"] == "Luna"
    assert data["lust"] == 0

    # 2. Read
    response = client.get(f"/characters/{char_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Luna"

    # 3. List
    response = client.get("/characters/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 4. Update
    response = client.put(f"/characters/{char_id}", json={
        "name": "Luna Updated",
        "description": "A mysterious space traveler.",
        "lust": 80
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Luna Updated"
    assert data["lust"] == 80

    # 5. Delete
    response = client.delete(f"/characters/{char_id}")
    assert response.status_code == 200
    
    response = client.get(f"/characters/{char_id}")
    assert response.status_code == 404

def test_character_creation_with_lust(client, db_session):
    """Character created with a lust value should persist it."""
    response = client.post("/characters/", json={
        "name": "Selene",
        "description": "A seductive siren.",
        "lust": 90
    })
    assert response.status_code == 200
    data = response.json()
    assert data["lust"] == 90

    # Verify it persists on read
    char_id = data["id"]
    response = client.get(f"/characters/{char_id}")
    assert response.json()["lust"] == 90

def test_character_update_preserves_lust(client, db_session):
    """Updating a character should preserve or update lust."""
    response = client.post("/characters/", json={
        "name": "Test",
        "description": "Test character",
        "lust": 50
    })
    char_id = response.json()["id"]

    # Update with new lust value
    response = client.put(f"/characters/{char_id}", json={
        "name": "Test Updated",
        "description": "Updated description",
        "lust": 20
    })
    assert response.status_code == 200
    assert response.json()["lust"] == 20

def test_tag_assignment(client, db_session):
    # Setup: Create a tag
    tag = Tag(label="Playful", instruction="Be more playful.")
    db_session.add(tag)
    db_session.commit()
    tag_id = tag.id

    # Create character with tag
    response = client.post("/characters/", json={
        "name": "Gemi",
        "description": "Feisty entity",
        "tag_ids": [tag_id]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["label"] == "Playful"

def test_auto_tag_generation(client, db_session):
    # Mocking LLM suggestion (Profiler uses suggestions)
    from unittest.mock import patch
    with patch("app.core.profiler.Profiler.suggest_tags") as mock_suggest:
        mock_suggest.return_value = [1] # Assume tag 1 is suggested
        
        response = client.post("/characters/auto-tag", json={
            "description": "A very friendly and helpful robot."
        })
        assert response.status_code == 200
        assert response.json() == [1]
