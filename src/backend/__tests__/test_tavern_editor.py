import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.backend.db.models import Character, AgentState
from src.backend.core.orchestration.bridge import Brain


def test_tokenize_endpoint(client):
    with patch(
        "src.backend.core.context.budget.ContextBudgetCalculator.count_tokens",
        new_callable=AsyncMock,
    ) as mock_count:
        mock_count.return_value = 12

        response = client.post("/settings/tokenize", json={"text": "Hello world!"})
        assert response.status_code == 200
        assert response.json() == {"tokens": 12}
        mock_count.assert_called_with("Hello world!")


def test_parse_png_endpoint(client):
    from src.backend.core.importer.png_parser import TavernV2Card, TavernV2Data

    card_data = TavernV2Data(
        name="TavernBot",
        description="A helpful assistant.",
        personality="Helpful and polite.",
        scenario="A cozy workshop.",
        first_mes="Greetings! How can I assist you today?",
        mes_example="user: hi\nbot: hello!",
    )
    mock_card = TavernV2Card(data=card_data)

    with patch(
        "src.backend.core.importer.png_parser.parse_png_character_card",
        return_value=mock_card,
    ):
        response = client.post(
            "/characters/parse-png",
            files={"file": ("bot.png", b"fake-png-data", "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TavernBot"
        assert data["description"] == "A helpful assistant."
        assert data["personality"] == "Helpful and polite."
        assert data["scenario"] == "A cozy workshop."
        assert data["first_mes"] == "Greetings! How can I assist you today?"
        assert data["mes_example"] == "user: hi\nbot: hello!"


def test_create_character_expanded_fields(client, db_session):
    payload = {
        "name": "Kaelen",
        "description": "Short bio description.",
        "nickname": "Kael",
        "short_description": "Bio for sidebar.",
        "persona_prompt": "Quiet and observant.",
        "scenario": "Under a shady oak tree.",
        "first_mes": "What brings you here?",
        "mes_example": "user: hello\nKaele: *nods*",
        "content_rating": "limitless",
    }
    response = client.post("/characters/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Kaelen"
    assert data["nickname"] == "Kael"
    assert data["content_rating"] == "limitless"

    # Verify db state
    char = db_session.query(Character).filter(Character.id == data["id"]).first()
    assert char is not None
    assert char.nickname == "Kael"
    assert char.scenario == "Under a shady oak tree."
    assert char.first_mes == "What brings you here?"
    assert char.mes_example == "user: hello\nKaele: *nods*"
    assert char.content_rating == "limitless"


def test_update_character_expanded_fields(client, db_session):
    char = Character(name="OldName", description="OldDesc")
    db_session.add(char)
    db_session.commit()

    payload = {
        "name": "UpdatedName",
        "description": "UpdatedDesc",
        "nickname": "UpNick",
        "short_description": "UpdatedShort",
        "persona_prompt": "UpdatedPersona",
        "scenario": "UpdatedScenario",
        "first_mes": "UpdatedFirst",
        "mes_example": "UpdatedExample",
        "content_rating": "limitless",
    }
    response = client.put(f"/characters/{char.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "UpNick"

    db_session.refresh(char)
    assert char.nickname == "UpNick"
    assert char.scenario == "UpdatedScenario"
    assert char.first_mes == "UpdatedFirst"
    assert char.mes_example == "UpdatedExample"
    assert char.content_rating == "limitless"


@pytest.mark.asyncio
async def test_prompt_construction_with_expanded_fields():
    mock_vector = MagicMock()
    mock_vector.query_memory = AsyncMock(return_value={"documents": [[]]})
    mock_vector.query_lore = MagicMock()
    mock_vector.query_lore.documents = [[]]
    mock_vector.llm_client = MagicMock()
    mock_vector.llm_client.url = "http://127.0.0.1:8080"

    brain = Brain(vector_store=mock_vector)

    class MockChar:
        id = 10
        name = "Kaelen"
        description = "A standard description."
        short_description = "A custom short bio."
        nickname = "Kael"
        persona_prompt = "Observant and calm."
        scenario = "Resting in a tavern."
        first_mes = "Welcome."
        mes_example = "user: hi\nKael: *looks up*"
        tags = []

    state = {
        "location": "Tavern",
        "mood": "Calm",
        "stats": {
            "energy": 90,
            "hunger": 10,
            "happiness": 80,
            "social": 80,
            "relationship": {"score": 60},
        },
    }

    prompt = await brain.build_prompt("Hello!", MockChar(), state)
    assert "Identity: Kael. A custom short bio." in prompt
    assert "Personality: Observant and calm." in prompt
    assert "Scenario: Resting in a tavern." in prompt
    assert "Example Dialogs:\nuser: hi\nKael: *looks up*" in prompt


def test_upload_avatar_endpoint(client, db_session, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    char = Character(name="AvatarChar", description="No avatar yet")
    db_session.add(char)
    db_session.commit()

    response = client.post(
        f"/characters/{char.id}/avatar",
        files={"file": ("avatar.png", b"\x89PNG\r\n\x1a\nfake-avatar", "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["avatar_url"] == f"/avatars/{char.id}.png"

    # Verify avatar saved to disk
    avatar_file = tmp_path / "static" / "avatars" / f"{char.id}.png"
    assert avatar_file.exists()
