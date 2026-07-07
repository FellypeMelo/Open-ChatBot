from src.backend.db.models import Character, User, AgentState


def test_chat_with_missing_character(client, db_session):
    # Endpoint should create a default character if ID not found
    from unittest.mock import patch, AsyncMock

    with (
        patch(
            "src.backend.core.orchestration.bridge.VectorStore.query_memory",
            new_callable=AsyncMock,
        ) as mock_query,
        patch("src.backend.core.engine.llm.LlamaClient.complete") as mock_complete,
    ):
        mock_query.return_value = {}
        mock_complete.return_value = {"content": '*Nods.* "Hello there."'}

        response = client.post("/chat", json={"message": "hi", "character_id": 999})
        assert (
            response.status_code == 200
        )  # Should fallback to default character creation
        assert "stats" in response.json()


def test_chat_with_corrupted_stats(client, db_session):
    # Setup character with empty/corrupted stats
    char = Character(id=5, name="Broken", description="Broken")
    db_session.add(char)
    state = AgentState(character_id=5, stats={})  # Empty dict
    db_session.add(state)
    db_session.commit()

    from unittest.mock import patch, AsyncMock

    with (
        patch(
            "src.backend.core.orchestration.bridge.VectorStore.query_memory",
            new_callable=AsyncMock,
        ) as mock_query,
        patch("src.backend.core.engine.llm.LlamaClient.complete") as mock_complete,
    ):
        mock_query.return_value = {}
        mock_complete.return_value = {"content": '*Smiles.* "Hey."'}

        response = client.post("/chat", json={"message": "hi", "character_id": 5})
        assert response.status_code == 200
        # Check if ensure_stats_integrity worked
        assert "energy" in response.json()["stats"]


def test_user_creation_on_first_chat(client, db_session):
    # Ensure no users exist
    db_session.query(User).delete()
    db_session.commit()

    char = Character(id=1, name="Gemi", description="Test")
    db_session.add(char)
    db_session.commit()

    from unittest.mock import patch, AsyncMock

    with (
        patch(
            "src.backend.core.orchestration.bridge.VectorStore.query_memory",
            new_callable=AsyncMock,
        ) as mock_query,
        patch("src.backend.core.engine.llm.LlamaClient.complete") as mock_complete,
    ):
        mock_query.return_value = {}
        mock_complete.return_value = {"content": '*Waves.* "Hi there!"'}

        response = client.post("/chat", json={"message": "hi", "character_id": 1})
        assert response.status_code == 200

        # Verify user was created
        user = db_session.query(User).first()
        assert user is not None
        assert user.name == "User"
