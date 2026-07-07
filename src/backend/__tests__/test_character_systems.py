import pytest
from src.backend.db.models import Tag


def test_character_crud(client, db_session):
    # 1. Create
    response = client.post(
        "/characters/",
        json={"name": "Luna", "description": "A mysterious space traveler."},
    )
    assert response.status_code == 200
    data = response.json()
    char_id = data["id"]
    assert data["name"] == "Luna"

    # 2. Read
    response = client.get(f"/characters/{char_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Luna"

    # 3. List
    response = client.get("/characters/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 4. Update
    response = client.put(
        f"/characters/{char_id}",
        json={"name": "Luna Updated", "description": "A mysterious space traveler."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Luna Updated"

    # 5. Delete
    response = client.delete(f"/characters/{char_id}")
    assert response.status_code == 200

    response = client.get(f"/characters/{char_id}")
    assert response.status_code == 404


def test_tag_assignment(client, db_session):
    # Setup: Create a tag
    tag = Tag(label="Playful", instruction="Be more playful.")
    db_session.add(tag)
    db_session.commit()
    tag_id = tag.id

    # Create character with tag
    response = client.post(
        "/characters/",
        json={"name": "Gemi", "description": "Feisty entity", "tag_ids": [tag_id]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["label"] == "Playful"


def test_auto_tag_generation(client, db_session):
    # Mocking LLM suggestion (Profiler is now in Brain)
    from unittest.mock import patch

    with patch(
        "src.backend.core.orchestration.bridge.Brain.suggest_tags"
    ) as mock_suggest:
        mock_suggest.return_value = [1]  # Assume tag 1 is suggested

        response = client.post(
            "/characters/auto-tag",
            json={"description": "A very friendly and helpful robot."},
        )
        assert response.status_code == 200
        assert response.json() == [1]


@pytest.mark.asyncio
async def test_brain_reflection():
    from src.backend.core.orchestration.bridge import Brain
    from unittest.mock import AsyncMock, MagicMock
    import json

    mock_vector = MagicMock()
    mock_llm = AsyncMock()
    brain = Brain(vector_store=mock_vector, llm_client=mock_llm)

    response_data = {
        "summary": "Pizza talk.",
        "facts": ["Likes pizza"],
        "traits": ["hungry"],
    }
    mock_llm.complete.return_value = {"content": json.dumps(response_data)}

    result = await brain.reflect([{"role": "user", "content": "I like pizza"}])
    assert result["summary"] == "Pizza talk."
    assert "hungry" in result["traits"]
