from unittest.mock import patch


def test_grammar_not_passed_to_llm_complete(client, db_session):
    """Grammar constraint should NOT be passed (removed for low-end model compat)."""
    from src.backend.db.models import Character, User, AgentState

    char = Character(id=2, name="Luna", description="Test")
    db_session.add(char)
    user = User(name="Alice", gender="Female", is_active=True)
    db_session.add(user)
    state = AgentState(character_id=2)
    db_session.add(state)
    db_session.commit()

    with (
        patch("src.backend.core.engine.llm.LlamaClient.complete") as mock_complete,
        patch(
            "src.backend.core.orchestration.bridge.Brain.build_prompt"
        ) as mock_prompt,
    ):
        mock_prompt.return_value = "Prompt"
        mock_complete.return_value = {"content": '*She looks up.* "Hi there!"'}

        client.post("/chat", json={"message": "hello", "character_id": 2})

        # Verify NO grammar was passed (it should be None or absent)
        assert len(mock_complete.call_args_list) >= 1
        _args, first_kwargs = mock_complete.call_args_list[0]
        grammar = first_kwargs.get("grammar")
        assert grammar is None
