"""Coverage for the ChatTurnContext/_prepare_chat_turn refactor of chat.py:
the shared setup helper, the /chat/actions endpoint, action-stat clamping,
the stale-data (409) conflict path on both /chat and /chat/stream, the
chat_stream setup-failure error payload, the "regenerate" (parent_id, no
message) persistence bug fix, preset selection, and the message edit/delete
endpoints -- none of which had dedicated tests before this refactor.
"""

import os
import tempfile
from contextlib import contextmanager

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import StaleDataError
from fastapi.testclient import TestClient

from src.backend.db.database import Base, get_db
from src.backend.db.models import AgentState, Chat, Character, MessageNode, SamplerPreset
from src.backend.api import chat as chat_module
from src.backend.api.chat import LLMConfig
from src.backend.core.engine.state_transitions import ACTIONS_CONFIG, apply_action_stats
from src.backend.main import app


@contextmanager
def isolated_client():
    """A TestClient backed by its own file-based engine + a fresh session per
    request (mirroring production's per-request SessionLocal()), for tests
    that simulate a StaleDataError conflict. The shared client/db_session
    fixture wraps a whole test in one external transaction, so the app's own
    db.rollback() on a simulated conflict would wipe that fixture's own setup
    rows too -- something that can never happen in production, where every
    request gets an independent session/transaction. Yields (client,
    TestSessionLocal) so the caller can both drive requests and set up/verify
    rows directly.
    """
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, TestSessionLocal
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        os.close(db_fd)
        try:
            os.unlink(db_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# GET /chat/actions
# ---------------------------------------------------------------------------


def test_list_actions_returns_message_for_every_configured_action(client):
    resp = client.get("/chat/actions")
    assert resp.status_code == 200
    data = resp.json()

    assert set(data.keys()) == set(ACTIONS_CONFIG.keys())
    for action_id, cfg in ACTIONS_CONFIG.items():
        assert data[action_id] == cfg["message"]
        # The endpoint must never leak internal stat deltas to the client.
        assert "stats" not in data


# ---------------------------------------------------------------------------
# _apply_action_stats: clamping + non-dict relationship fallback
# ---------------------------------------------------------------------------


def test_apply_action_stats_clamps_between_0_and_100():
    stats = {
        "energy": 95,
        "hunger": 5,
        "happiness": 98,
        "social": 97,
        "relationship": {"score": 95},
    }
    stat_mod = {
        "energy": 20,
        "hunger": -20,
        "happiness": 10,
        "social": 15,
        "relationship_score": 20,
    }
    result = apply_action_stats(stats, stat_mod)

    assert result["energy"] == 100
    assert result["hunger"] == 0
    assert result["happiness"] == 100
    assert result["social"] == 100
    assert result["relationship"]["score"] == 100


def test_apply_action_stats_relationship_non_dict_falls_back_to_default_score():
    stats = {
        "energy": 50,
        "hunger": 50,
        "happiness": 50,
        "social": 50,
        "relationship": "corrupted-legacy-value",
    }
    result = apply_action_stats(stats, {"relationship_score": 5})

    assert result["relationship"] == {"score": 55}


def test_apply_action_stats_handles_missing_stats_dict():
    result = apply_action_stats(None, {"energy": 10, "hunger": -5})

    assert result["energy"] == 100  # default 100 + 10, clamped
    assert result["hunger"] == 0  # default 0 - 5, clamped
    assert result["relationship"] == {"score": 50}


# ---------------------------------------------------------------------------
# LLMConfig.base_url validator
# ---------------------------------------------------------------------------


def test_llm_config_base_url_allows_falsy_and_loopback_rejects_remote_host():
    assert LLMConfig(base_url=None).base_url is None
    assert LLMConfig(base_url="").base_url == ""
    assert (
        LLMConfig(base_url="http://127.0.0.1:8080").base_url == "http://127.0.0.1:8080"
    )
    assert (
        LLMConfig(base_url="http://localhost:8080").base_url == "http://localhost:8080"
    )

    with pytest.raises(ValidationError, match="loopback"):
        LLMConfig(base_url="http://example.com:1234")


# ---------------------------------------------------------------------------
# Regenerate (parent_id, no message) -- the persisted interaction/decay bug fix
# ---------------------------------------------------------------------------


def test_regenerate_without_message_persists_interaction_count_and_stat_decay(
    client, db_session
):
    char = Character(id=509, name="RegenChar", description="Desc")
    db_session.add(char)
    db_session.commit()

    stale_timestamp = (datetime.now(timezone.utc) - timedelta(hours=4.9)).isoformat()
    state = AgentState(
        character_id=509,
        interaction_count=7,
        stats={
            "energy": 100,
            "hunger": 0,
            "happiness": 100,
            "social": 100,
            "is_sleeping": False,
            "last_update": stale_timestamp,
            "relationship": {"score": 50},
        },
    )
    db_session.add(state)
    db_session.commit()

    user_msg = MessageNode(
        character_id=509, role="user", content="What's up?", is_active=True
    )
    db_session.add(user_msg)
    db_session.commit()
    state.current_message_id = user_msg.id
    db_session.commit()

    with patch(
        "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = {"content": "Just relaxing here with you."}

        # Regenerate: parent_id references the existing user turn, no new
        # message text is sent.
        resp = client.post(
            "/chat", json={"character_id": 509, "parent_id": user_msg.id}
        )

    assert resp.status_code == 200

    refreshed = (
        db_session.query(AgentState).filter(AgentState.character_id == 509).first()
    )
    # This is the exact bug that was fixed: previously, a message-less
    # regenerate call never reached the commit that persists the interaction
    # count / need-decay bump, so it was silently lost once the session
    # closed at the end of the request.
    assert refreshed.interaction_count == 8
    assert refreshed.stats["hunger"] == 49
    assert refreshed.stats["energy"] == 75
    assert refreshed.stats["social"] == 75
    assert refreshed.stats["happiness"] == 90

    # A bare regenerate call must not create a second user message.
    user_messages = (
        db_session.query(MessageNode)
        .filter(MessageNode.character_id == 509, MessageNode.role == "user")
        .all()
    )
    assert len(user_messages) == 1


def test_regenerate_does_not_duplicate_user_message_in_prompt(client, db_session):
    """RP bug: on a regenerate (no message, parent_id -> last user turn), the
    history walk ends on that user line AND build_prompt re-appends it as the
    trailing 'User:' turn, so the model saw the user's last line twice. The
    trailing line must be dropped from the history slice."""
    char = Character(id=514, name="RegenPromptChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(
        character_id=514,
        interaction_count=1,
        stats={
            "energy": 100,
            "hunger": 0,
            "happiness": 100,
            "social": 100,
            "is_sleeping": False,
            "last_update": datetime.now(timezone.utc).isoformat(),
            "relationship": {"score": 50},
        },
    )
    db_session.add(state)
    db_session.commit()
    user_msg = MessageNode(
        character_id=514, role="user", content="tell me a secret", is_active=True
    )
    db_session.add(user_msg)
    db_session.commit()
    state.current_message_id = user_msg.id
    db_session.commit()

    captured = {}

    async def fake_build_prompt(user_message, character, state_dict, **kwargs):
        captured["user_message"] = user_message
        captured["history"] = kwargs.get("history") or []
        return "PROMPT"

    with patch(
        "src.backend.api.chat.brain.build_prompt",
        new=AsyncMock(side_effect=fake_build_prompt),
    ), patch(
        "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = {"content": "A whispered secret."}
        resp = client.post("/chat", json={"character_id": 514, "parent_id": user_msg.id})

    assert resp.status_code == 200
    # build_prompt appends the user line as the trailing turn, so it must NOT
    # also appear inside the history slice.
    dupes = [
        m
        for m in captured["history"]
        if m.get("role") == "user" and m.get("content") == "tell me a secret"
    ]
    assert dupes == [], "regenerate duplicated the user message into history"
    assert captured["user_message"] == "tell me a secret"


def test_chat_history_walk_stops_at_missing_ancestor(client, db_session):
    char = Character(id=502, name="OrphanChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=502)
    db_session.add(state)
    db_session.commit()

    with patch(
        "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = {"content": "fine"}
        # parent_id points at a message that does not exist -- the history
        # walk must stop (break) instead of looping or erroring.
        resp = client.post(
            "/chat",
            json={"character_id": 502, "message": "hello", "parent_id": 999999},
        )

    assert resp.status_code == 200
    assert resp.json()["reply"] == "fine"


# ---------------------------------------------------------------------------
# Sampler preset selection (explicit preset_id + is_default fallback)
# ---------------------------------------------------------------------------


def test_chat_uses_explicit_preset_and_falls_back_to_default(client, db_session):
    char = Character(id=501, name="PresetChar", description="Desc")
    db_session.add(char)
    default_preset = SamplerPreset(
        name="DefaultPreset501", is_default=True, temperature=0.9
    )
    custom_preset = SamplerPreset(
        name="CustomPreset501", is_default=False, temperature=1.3, top_k=50
    )
    db_session.add(default_preset)
    db_session.add(custom_preset)
    db_session.commit()

    state = AgentState(character_id=501)
    db_session.add(state)
    db_session.commit()

    with patch(
        "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = {"content": "ok"}

        # No preset_id -> falls back to the row flagged is_default.
        resp = client.post("/chat", json={"character_id": 501, "message": "hi"})
        assert resp.status_code == 200
        _, kwargs = mock_complete.call_args
        assert kwargs["preset"]["temperature"] == 0.9

        # Explicit preset_id -> looks up that specific row instead.
        resp = client.post(
            "/chat",
            json={
                "character_id": 501,
                "message": "hi again",
                "config": {"preset_id": custom_preset.id},
            },
        )
        assert resp.status_code == 200
        _, kwargs = mock_complete.call_args
        assert kwargs["preset"]["temperature"] == 1.3
        assert kwargs["preset"]["top_k"] == 50


# ---------------------------------------------------------------------------
# Stale-data conflict -> 409 (both endpoints)
# ---------------------------------------------------------------------------


def test_chat_commit_conflict_returns_409():
    with isolated_client() as (iso_client, TestSessionLocal):
        setup_db = TestSessionLocal()
        char = Character(id=506, name="ConflictChar", description="Desc")
        setup_db.add(char)
        setup_db.commit()
        state = AgentState(character_id=506)
        setup_db.add(state)
        setup_db.commit()
        setup_db.close()

        with patch(
            "sqlalchemy.orm.Session.commit", side_effect=StaleDataError("stale")
        ):
            resp = iso_client.post("/chat", json={"character_id": 506, "message": "hi"})

        assert resp.status_code == 409
        assert "concurrently" in resp.json()["detail"].lower()


def test_chat_stream_commit_conflict_reports_error_in_stream():
    with isolated_client() as (iso_client, TestSessionLocal):
        setup_db = TestSessionLocal()
        char = Character(id=507, name="StreamConflictChar", description="Desc")
        setup_db.add(char)
        setup_db.commit()
        state = AgentState(character_id=507)
        setup_db.add(state)
        setup_db.commit()
        setup_db.close()

        with patch(
            "sqlalchemy.orm.Session.commit", side_effect=StaleDataError("stale")
        ):
            resp = iso_client.post(
                "/chat/stream", json={"character_id": 507, "message": "hi"}
            )
            content = b"".join(resp.iter_bytes())

        # Fixed: /chat/stream now passes status_code=409 to StreamingResponse,
        # matching /chat's HTTPException(409) for the same stale-data conflict.
        assert resp.status_code == 409
        assert b"error" in content
        assert b"concurrently" in content


def test_chat_stream_setup_failure_yields_error_not_raw_500(client, db_session):
    char = Character(id=508, name="SetupFailChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=508)
    db_session.add(state)
    db_session.commit()

    with patch(
        "src.backend.api.chat.brain.build_prompt",
        new_callable=AsyncMock,
        side_effect=Exception("prompt builder exploded"),
    ):
        resp = client.post("/chat/stream", json={"character_id": 508, "message": "hi"})
        content = b"".join(resp.iter_bytes())

    assert resp.status_code == 200
    assert b"error" in content
    assert b"prompt builder exploded" in content


# ---------------------------------------------------------------------------
# chat_stream success path: persists the reply + updated AgentState
# ---------------------------------------------------------------------------


def test_chat_stream_success_persists_reply_and_updates_agent_state(
    client, db_session, monkeypatch
):
    char = Character(id=511, name="StreamSuccessChar", description="Desc")
    db_session.add(char)
    db_session.commit()

    state = AgentState(
        character_id=511,
        stats={
            "energy": 90,
            "hunger": 5,
            "happiness": 95,
            "social": 95,
            "is_sleeping": False,
            "relationship": {"score": 50},
        },
    )
    db_session.add(state)
    db_session.commit()

    # chat_stream's success path opens its own SessionLocal() to persist the
    # assistant reply after the token stream finishes. Point that at this
    # test's isolated session instead of the real chatbot.db engine -- never
    # let the endpoint's background SessionLocal() touch production data.
    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    with patch(
        "src.backend.core.engine.llm.LlamaClient.complete_stream"
    ) as mock_stream:

        async def mock_iter(prompt, url=None, model=None, preset=None):
            yield "*I smile.* "
            yield "**enters the Kitchen** "
            yield "Hello there!"

        mock_stream.side_effect = mock_iter

        resp = client.post("/chat/stream", json={"character_id": 511, "message": "hi"})
        content = b"".join(resp.iter_bytes())

    assert resp.status_code == 200
    assert b'"done": true' in content
    assert b"message_id" in content

    ai_msg = (
        db_session.query(MessageNode)
        .filter(MessageNode.character_id == 511, MessageNode.role == "assistant")
        .first()
    )
    assert ai_msg is not None
    assert "Hello there!" in ai_msg.content

    refreshed_state = (
        db_session.query(AgentState).filter(AgentState.character_id == 511).first()
    )
    assert refreshed_state.location == "Kitchen"
    assert refreshed_state.current_message_id == ai_msg.id


def test_chat_stream_reply_failing_formatting_logs_warning(
    client, db_session, monkeypatch
):
    char = Character(id=514, name="UnformattedReplyChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=514)
    db_session.add(state)
    db_session.commit()

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    # RN-003 requires a *thought* and a **action** marker once a reply passes
    # 50 words -- this reply is plain prose, so it must fail validation and
    # log a warning (rather than raise) from within the streaming success path.
    long_plain_reply = " ".join(["word"] * 60)

    with patch(
        "src.backend.core.engine.llm.LlamaClient.complete_stream"
    ) as mock_stream:

        async def mock_iter(prompt, url=None, model=None, preset=None):
            yield long_plain_reply

        mock_stream.side_effect = mock_iter

        with patch.object(chat_module, "logger") as mock_logger:
            resp = client.post(
                "/chat/stream", json={"character_id": 514, "message": "hi"}
            )
            content = b"".join(resp.iter_bytes())

    assert resp.status_code == 200
    assert b'"done": true' in content
    assert any(
        "RN-003" in str(call.args[0]) for call in mock_logger.warning.call_args_list
    )


def test_chat_stream_empty_reply_yields_done_without_persisting(client, db_session):
    char = Character(id=512, name="EmptyReplyChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=512)
    db_session.add(state)
    db_session.commit()

    with patch(
        "src.backend.core.engine.llm.LlamaClient.complete_stream"
    ) as mock_stream:

        async def mock_iter(prompt, url=None, model=None, preset=None):
            yield "   "

        mock_stream.side_effect = mock_iter

        resp = client.post("/chat/stream", json={"character_id": 512, "message": "hi"})
        content = b"".join(resp.iter_bytes())

    assert resp.status_code == 200
    assert b'"done": true' in content
    assert b"error" not in content

    assistant_messages = (
        db_session.query(MessageNode)
        .filter(MessageNode.character_id == 512, MessageNode.role == "assistant")
        .all()
    )
    assert assistant_messages == []


# ---------------------------------------------------------------------------
# run_consciousness_layer: force_reflect branch (evolve_character call)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_consciousness_layer_force_reflect_evolves_character(
    db_session, monkeypatch
):
    char = Character(id=510, name="ReflectChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    state = AgentState(character_id=510)
    db_session.add(state)
    db_session.commit()

    # run_consciousness_layer opens its own SessionLocal() too -- reuse the
    # isolated test session rather than letting it fall through to chatbot.db.
    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    with (
        patch.object(
            chat_module.vector_store, "add_memory", new_callable=AsyncMock
        ) as mock_add_memory,
        patch.object(
            chat_module.brain, "reflect", new_callable=AsyncMock
        ) as mock_reflect,
        patch("src.backend.api.chat.evolve_character") as mock_evolve,
    ):
        mock_add_memory.return_value = None
        mock_reflect.return_value = {
            "summary": "A good chat.",
            "traits": {},
            "facts": [],
        }

        await chat_module.run_consciousness_layer(
            510, "hello", "hi there", force_reflect=True
        )

    mock_reflect.assert_called_once()
    mock_evolve.assert_called_once()
    args, _ = mock_evolve.call_args
    assert args[1] == 510


@pytest.mark.asyncio
async def test_run_consciousness_layer_reflection_excludes_inactive_messages(
    db_session, monkeypatch
):
    # Reflection must summarize only the live branch: an edited-away or
    # regenerated (is_active=False) node must never reach brain.reflect, or its
    # discarded content becomes permanent cross-chat canon (PZ-02).
    char = Character(id=511, name="ActiveOnlyChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    db_session.add(AgentState(character_id=511))
    db_session.commit()

    db_session.add(
        MessageNode(
            character_id=511,
            chat_id=77,
            role="user",
            content="ACTIVE user line",
            is_active=True,
        )
    )
    db_session.add(
        MessageNode(
            character_id=511,
            chat_id=77,
            role="assistant",
            content="DISCARDED variant",
            is_active=False,
        )
    )
    db_session.commit()

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    with (
        patch.object(chat_module.vector_store, "add_memory", new_callable=AsyncMock),
        patch.object(
            chat_module.brain, "reflect", new_callable=AsyncMock
        ) as mock_reflect,
        patch("src.backend.api.chat.evolve_character"),
    ):
        mock_reflect.return_value = {"summary": "s", "traits": {}, "facts": []}
        await chat_module.run_consciousness_layer(
            511, "hello", "hi", force_reflect=True, chat_id=77
        )

    mock_reflect.assert_called_once()
    passed_msgs, _ = mock_reflect.call_args
    contents = [m["content"] for m in passed_msgs[0]]
    assert "ACTIVE user line" in contents
    assert "DISCARDED variant" not in contents


@pytest.mark.asyncio
async def test_run_consciousness_layer_skips_memory_when_store_memory_false(
    db_session, monkeypatch
):
    # Quick-action turns pass store_memory=False so their canned first-person
    # text ("*I wrap my arms around you*") is never written as a User: memory,
    # where it would accumulate and self-retrieve on every repeat (PZ-04).
    char = Character(id=514, name="ActionChar", description="d")
    db_session.add(char)
    db_session.commit()
    db_session.add(AgentState(character_id=514))
    db_session.commit()

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    with patch.object(
        chat_module.vector_store, "add_memory", new_callable=AsyncMock
    ) as mock_add:
        await chat_module.run_consciousness_layer(
            514, "*I hug you*", "a reply", store_memory=False
        )

    mock_add.assert_not_awaited()


@pytest.mark.asyncio
async def test_run_consciousness_layer_purges_superseded_variant_memories(
    db_session, monkeypatch
):
    # PZ-01b: a regenerate creates a new sibling variant; only the selected
    # (latest) variant's memory should remain -- purge the superseded siblings.
    char = Character(id=521, name="RerollChar", description="d")
    db_session.add(char)
    db_session.commit()
    db_session.add(AgentState(character_id=521))
    db_session.commit()
    parent = MessageNode(character_id=521, role="user", content="hi", is_active=True)
    db_session.add(parent)
    db_session.commit()
    v1 = MessageNode(
        character_id=521, role="assistant", content="v1", parent_id=parent.id, is_active=True
    )
    v2 = MessageNode(
        character_id=521, role="assistant", content="v2", parent_id=parent.id, is_active=True
    )
    db_session.add_all([v1, v2])
    db_session.commit()
    # Capture ids before the call (run_consciousness_layer closes the session).
    v1_id, v2_id = v1.id, v2.id

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    with (
        patch.object(chat_module.vector_store, "add_memory", new_callable=AsyncMock),
        patch.object(
            chat_module.vector_store, "delete_by_message_ids", new_callable=AsyncMock
        ) as mock_del,
    ):
        await chat_module.run_consciousness_layer(
            521, "hi", "v2", chat_id=None, message_id=v2_id
        )

    mock_del.assert_awaited_once()
    purged = set(mock_del.call_args[0][0])
    assert v1_id in purged
    assert v2_id not in purged


@pytest.mark.asyncio
async def test_reflection_walks_active_branch_excluding_offbranch_variant(
    db_session, monkeypatch
):
    # PZ-02b: reflection walks the active branch from the selected leaf, so a
    # non-selected regenerate variant (off the chosen path) never enters the
    # permanent-state summary even though it is is_active=True.
    char = Character(id=522, name="BranchChar", description="d")
    db_session.add(char)
    db_session.commit()
    db_session.add(AgentState(character_id=522))
    db_session.commit()
    u = MessageNode(character_id=522, role="user", content="u-line", is_active=True)
    db_session.add(u)
    db_session.commit()
    chosen = MessageNode(
        character_id=522, role="assistant", content="CHOSEN", parent_id=u.id, is_active=True
    )
    offbranch = MessageNode(
        character_id=522, role="assistant", content="OFFBRANCH", parent_id=u.id, is_active=True
    )
    db_session.add_all([chosen, offbranch])
    db_session.commit()

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    with (
        patch.object(chat_module.vector_store, "add_memory", new_callable=AsyncMock),
        patch.object(
            chat_module.brain, "reflect", new_callable=AsyncMock
        ) as mock_reflect,
        patch("src.backend.api.chat.evolve_character"),
    ):
        mock_reflect.return_value = {"summary": "s", "traits": {}, "facts": []}
        await chat_module.run_consciousness_layer(
            522, "u-line", "CHOSEN", force_reflect=True, message_id=chosen.id
        )

    passed = [m["content"] for m in mock_reflect.call_args[0][0]]
    assert "CHOSEN" in passed
    assert "u-line" in passed
    assert "OFFBRANCH" not in passed


@pytest.mark.asyncio
async def test_run_consciousness_layer_marks_chat_last_reflected_count(
    db_session, monkeypatch
):
    # RF-04: a successful reflection records the consumed interaction count on the
    # reflecting Chat row (the per-chat source of truth), so a failed boundary
    # turn is retried next time instead of skipped forever.
    char = Character(id=525, name="MarkChar", description="d")
    db_session.add(char)
    db_session.commit()
    chat = Chat(character_id=525, title="C")
    db_session.add(chat)
    db_session.commit()
    chat_id = chat.id
    db_session.add(
        AgentState(character_id=525, interaction_count=20, active_chat_id=chat_id)
    )
    db_session.commit()

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(db_session, "close", lambda: None)

    with (
        patch.object(chat_module.vector_store, "add_memory", new_callable=AsyncMock),
        patch.object(
            chat_module.brain, "reflect", new_callable=AsyncMock
        ) as mock_reflect,
        patch("src.backend.api.chat.evolve_character"),
    ):
        mock_reflect.return_value = {"summary": "s", "traits": {}, "facts": []}
        await chat_module.run_consciousness_layer(
            525, "u", "a", force_reflect=True, chat_id=chat_id, reflected_at_count=20
        )

    refreshed_chat = db_session.query(Chat).filter_by(id=chat_id).first()
    assert refreshed_chat.last_reflected_at_count == 20


def test_chat_triggers_reflection_at_interval_via_range_check(client, db_session):
    # RF-04 (review #5): the range-check trigger in _prepare_chat_turn must fire a
    # reflection when interaction_count - last_reflected reaches the interval.
    from src.backend.core.config import settings

    char = Character(id=526, name="IntervalChar", description="d")
    db_session.add(char)
    db_session.commit()
    db_session.add(
        AgentState(
            character_id=526,
            interaction_count=settings.REFLECTION_INTERVAL - 1,
            last_reflected_at_count=0,
        )
    )
    db_session.commit()

    with (
        patch(
            "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
        ) as mock_complete,
        patch.object(chat_module, "run_consciousness_layer") as mock_rcl,
    ):
        mock_complete.return_value = {"content": "a reply"}
        resp = client.post("/chat", json={"character_id": 526, "message": "hi"})

    assert resp.status_code == 200
    mock_rcl.assert_called_once()
    assert mock_rcl.call_args.kwargs["force_reflect"] is True


@pytest.mark.asyncio
async def test_reflection_stamps_reflecting_chat_and_respects_active_chat_guard(
    db_session, monkeypatch
):
    # RF-04 (review #1/#2/#6): a reflection for chat A that finishes AFTER the
    # user switched to chat B must stamp chat A's row (the reflecting chat) but
    # NOT clobber the shared AgentState mirror (now belonging to chat B).
    char = Character(id=527, name="SwitchChar", description="d")
    db_session.add(char)
    db_session.commit()
    chat_a = Chat(character_id=527, title="A")
    chat_b = Chat(character_id=527, title="B")
    db_session.add_all([chat_a, chat_b])
    db_session.commit()
    chat_a_id, chat_b_id = chat_a.id, chat_b.id
    # Active chat is now B; the reflection being finished is for A.
    db_session.add(
        AgentState(
            character_id=527, active_chat_id=chat_b_id, last_reflected_at_count=0
        )
    )
    db_session.commit()

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(db_session, "close", lambda: None)

    with (
        patch.object(chat_module.vector_store, "add_memory", new_callable=AsyncMock),
        patch.object(
            chat_module.brain, "reflect", new_callable=AsyncMock
        ) as mock_reflect,
    ):
        mock_reflect.return_value = {"summary": "s", "traits": {}, "facts": []}
        await chat_module.run_consciousness_layer(
            527,
            "u",
            "a",
            force_reflect=True,
            chat_id=chat_a_id,
            reflected_at_count=20,
        )

    agent = db_session.query(AgentState).filter_by(character_id=527).first()
    reflecting_chat = db_session.query(Chat).filter_by(id=chat_a_id).first()
    # Chat A (reflecting) is stamped; the AgentState mirror (now chat B) is NOT.
    assert reflecting_chat.last_reflected_at_count == 20
    assert agent.last_reflected_at_count == 0


@pytest.mark.asyncio
async def test_run_consciousness_layer_tags_memory_with_message_id(
    db_session, monkeypatch
):
    # The memory carries the assistant message id so it can be purged when that
    # node is edited/deleted/regenerated away (PZ-01).
    char = Character(id=515, name="TagChar", description="d")
    db_session.add(char)
    db_session.commit()
    db_session.add(AgentState(character_id=515))
    db_session.commit()

    monkeypatch.setattr(chat_module, "SessionLocal", lambda: db_session)

    with patch.object(
        chat_module.vector_store, "add_memory", new_callable=AsyncMock
    ) as mock_add:
        await chat_module.run_consciousness_layer(
            515, "hi", "reply", chat_id=8, message_id=99
        )

    mock_add.assert_awaited_once()
    _args, kwargs = mock_add.call_args
    assert kwargs["metadata"]["message_id"] == 99


# ---------------------------------------------------------------------------
# /chat/clear/{character_id} resets AgentState to the documented defaults
# ---------------------------------------------------------------------------


def test_clear_chat_history_resets_all_agent_state_defaults(client, db_session):
    char = Character(id=513, name="ClearFullChar", description="Desc")
    db_session.add(char)
    db_session.commit()

    state = AgentState(
        character_id=513,
        location="Bedroom",
        clothes="Pajamas",
        mood="Grumpy",
        interaction_count=42,
        stats={
            "energy": 10,
            "hunger": 90,
            "happiness": 5,
            "social": 5,
            "is_sleeping": True,
            "relationship": {"score": 12},
        },
    )
    db_session.add(state)
    db_session.commit()
    state.current_message_id = None
    db_session.commit()

    resp = client.post(f"/chat/clear/{char.id}")
    assert resp.status_code == 200

    refreshed = (
        db_session.query(AgentState).filter(AgentState.character_id == 513).first()
    )
    assert refreshed.current_message_id is None
    assert refreshed.location == "Living Room"
    assert refreshed.clothes == "Casual"
    assert refreshed.mood == "Neutral"
    assert refreshed.interaction_count == 0
    # last_update is a live timestamp (required so needs can decay after a
    # reset); assert it exists + is ISO-parseable, then compare the rest.
    assert "last_update" in refreshed.stats
    from datetime import datetime as _dt

    _dt.fromisoformat(refreshed.stats["last_update"])
    stats_no_ts = {k: v for k, v in refreshed.stats.items() if k != "last_update"}
    assert stats_no_ts == {
        "energy": 100,
        "hunger": 0,
        "happiness": 100,
        "social": 100,
        "is_sleeping": False,
        "relationship": {"score": 50, "history": [], "nickname": None},
    }


# ---------------------------------------------------------------------------
# PUT/DELETE /chat/message/{id}
# ---------------------------------------------------------------------------


def test_edit_user_message_deactivates_subtree_and_advances_current_message(
    client, db_session
):
    char = Character(id=503, name="EditChar", description="Desc")
    db_session.add(char)
    db_session.commit()

    root = MessageNode(character_id=503, role="user", content="Hi", is_active=True)
    db_session.add(root)
    db_session.commit()

    reply = MessageNode(
        character_id=503,
        role="assistant",
        content="Hello!",
        parent_id=root.id,
        is_active=True,
    )
    db_session.add(reply)
    db_session.commit()

    followup = MessageNode(
        character_id=503,
        role="user",
        content="How are you?",
        parent_id=reply.id,
        is_active=True,
    )
    db_session.add(followup)
    db_session.commit()

    state = AgentState(character_id=503, current_message_id=followup.id)
    db_session.add(state)
    db_session.commit()

    resp = client.put(f"/chat/message/{root.id}", json={"content": "Hi there, edited"})
    assert resp.status_code == 200

    refreshed_root = db_session.query(MessageNode).filter_by(id=root.id).first()
    refreshed_reply = db_session.query(MessageNode).filter_by(id=reply.id).first()
    refreshed_followup = db_session.query(MessageNode).filter_by(id=followup.id).first()
    refreshed_state = db_session.query(AgentState).filter_by(character_id=503).first()

    assert refreshed_root.content == "Hi there, edited"
    assert refreshed_reply.is_active is False
    assert refreshed_followup.is_active is False
    assert refreshed_state.current_message_id == root.id


def test_edit_assistant_message_does_not_deactivate_subtree(client, db_session):
    char = Character(id=504, name="EditAssistantChar", description="Desc")
    db_session.add(char)
    db_session.commit()

    root = MessageNode(character_id=504, role="user", content="Hi", is_active=True)
    db_session.add(root)
    db_session.commit()

    reply = MessageNode(
        character_id=504,
        role="assistant",
        content="Hello!",
        parent_id=root.id,
        is_active=True,
    )
    db_session.add(reply)
    db_session.commit()

    resp = client.put(f"/chat/message/{reply.id}", json={"content": "Hello there!"})
    assert resp.status_code == 200

    refreshed_reply = db_session.query(MessageNode).filter_by(id=reply.id).first()
    assert refreshed_reply.content == "Hello there!"
    assert refreshed_reply.is_active is True  # only user-message edits deactivate


def test_edit_message_not_found_returns_404(client, db_session):
    resp = client.put("/chat/message/999999", json={"content": "no-op"})
    assert resp.status_code == 404


def test_delete_message_deactivates_subtree_and_resets_current_message_to_parent(
    client, db_session
):
    char = Character(id=505, name="DeleteChar", description="Desc")
    db_session.add(char)
    db_session.commit()

    root = MessageNode(character_id=505, role="user", content="Hi", is_active=True)
    db_session.add(root)
    db_session.commit()

    reply = MessageNode(
        character_id=505,
        role="assistant",
        content="Hello!",
        parent_id=root.id,
        is_active=True,
    )
    db_session.add(reply)
    db_session.commit()

    grandchild = MessageNode(
        character_id=505,
        role="user",
        content="Cool",
        parent_id=reply.id,
        is_active=True,
    )
    db_session.add(grandchild)
    db_session.commit()

    state = AgentState(character_id=505, current_message_id=reply.id)
    db_session.add(state)
    db_session.commit()

    resp = client.delete(f"/chat/message/{reply.id}")
    assert resp.status_code == 200

    refreshed_reply = db_session.query(MessageNode).filter_by(id=reply.id).first()
    refreshed_grandchild = (
        db_session.query(MessageNode).filter_by(id=grandchild.id).first()
    )
    refreshed_state = db_session.query(AgentState).filter_by(character_id=505).first()

    assert refreshed_reply.is_active is False
    assert refreshed_grandchild.is_active is False
    assert refreshed_state.current_message_id == root.id


def test_delete_message_purges_vector_memory_for_deactivated_nodes(client, db_session):
    # PZ-01: deleting a message purges the RAG memories of the deleted node and
    # its subtree so discarded content can't resurface via retrieval.
    char = Character(id=516, name="PurgeChar", description="Desc")
    db_session.add(char)
    db_session.commit()
    root = MessageNode(character_id=516, role="user", content="Hi", is_active=True)
    db_session.add(root)
    db_session.commit()
    reply = MessageNode(
        character_id=516,
        role="assistant",
        content="Hello!",
        parent_id=root.id,
        is_active=True,
    )
    db_session.add(reply)
    db_session.commit()
    follow = MessageNode(
        character_id=516,
        role="user",
        content="More",
        parent_id=reply.id,
        is_active=True,
    )
    db_session.add(follow)
    db_session.commit()

    with patch.object(
        chat_module.vector_store, "delete_by_message_ids", new_callable=AsyncMock
    ) as mock_del:
        resp = client.delete(f"/chat/message/{reply.id}")

    assert resp.status_code == 200
    mock_del.assert_awaited_once()
    purged = set(mock_del.call_args[0][0])
    assert {reply.id, follow.id} <= purged


def test_edit_assistant_message_purges_its_stale_memory(client, db_session):
    # PZ-01 (review follow-up): editing an ASSISTANT reply must purge its memory,
    # which holds the pre-edit text -- otherwise the old content resurfaces.
    char = Character(id=518, name="EditAsstChar", description="d")
    db_session.add(char)
    db_session.commit()
    root = MessageNode(character_id=518, role="user", content="Hi", is_active=True)
    db_session.add(root)
    db_session.commit()
    reply = MessageNode(
        character_id=518,
        role="assistant",
        content="old text",
        parent_id=root.id,
        is_active=True,
    )
    db_session.add(reply)
    db_session.commit()

    with patch.object(
        chat_module.vector_store, "delete_by_message_ids", new_callable=AsyncMock
    ) as mock_del:
        resp = client.put(f"/chat/message/{reply.id}", json={"content": "new text"})

    assert resp.status_code == 200
    mock_del.assert_awaited_once()
    assert reply.id in set(mock_del.call_args[0][0])


def test_edit_user_message_purges_subtree_memories(client, db_session):
    # PZ-01 edit path (coverage): editing a USER turn purges its descendants'
    # memories (the replies it invalidated).
    char = Character(id=519, name="EditUserChar", description="d")
    db_session.add(char)
    db_session.commit()
    root = MessageNode(character_id=519, role="user", content="Hi", is_active=True)
    db_session.add(root)
    db_session.commit()
    reply = MessageNode(
        character_id=519,
        role="assistant",
        content="a reply",
        parent_id=root.id,
        is_active=True,
    )
    db_session.add(reply)
    db_session.commit()

    with patch.object(
        chat_module.vector_store, "delete_by_message_ids", new_callable=AsyncMock
    ) as mock_del:
        resp = client.put(f"/chat/message/{root.id}", json={"content": "Hi (edited)"})

    assert resp.status_code == 200
    mock_del.assert_awaited_once()
    assert reply.id in set(mock_del.call_args[0][0])


def test_chat_schedules_consciousness_with_message_id_and_store_memory(
    client, db_session
):
    # PZ-01/PZ-04 wiring (coverage): a real /chat turn must schedule the
    # consciousness layer with the assistant message_id and store_memory=True,
    # or both fixes silently no-op end to end.
    char = Character(id=520, name="WireChar", description="d")
    db_session.add(char)
    db_session.commit()
    db_session.add(AgentState(character_id=520))
    db_session.commit()

    with (
        patch(
            "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
        ) as mock_complete,
        patch.object(chat_module, "run_consciousness_layer") as mock_rcl,
    ):
        mock_complete.return_value = {"content": "A reply."}
        resp = client.post("/chat", json={"character_id": 520, "message": "hi"})

    assert resp.status_code == 200
    mock_rcl.assert_called_once()
    kwargs = mock_rcl.call_args.kwargs
    assert isinstance(kwargs["message_id"], int)
    assert kwargs["store_memory"] is True


def test_chat_empty_reply_stores_no_memory(client, db_session):
    # PZ-07: an empty/failed non-stream reply must not persist an assistant node
    # or store a "User: ..\nAI: " memory (the stream path already guards this).
    char = Character(id=523, name="EmptyReplyChar", description="d")
    db_session.add(char)
    db_session.commit()
    db_session.add(AgentState(character_id=523))
    db_session.commit()

    with (
        patch(
            "src.backend.core.engine.llm.LlamaClient.complete", new_callable=AsyncMock
        ) as mock_complete,
        patch.object(chat_module, "run_consciousness_layer") as mock_rcl,
    ):
        mock_complete.return_value = {"content": "   "}
        resp = client.post("/chat", json={"character_id": 523, "message": "hi"})

    assert resp.status_code == 200
    mock_rcl.assert_not_called()
    assistant_nodes = (
        db_session.query(MessageNode)
        .filter(MessageNode.character_id == 523, MessageNode.role == "assistant")
        .all()
    )
    assert assistant_nodes == []

    # TF-01 (decision: keep on failure): the user's message survives and the
    # pointer rests on it, so the turn is cleanly retryable/regenerable.
    user_node = (
        db_session.query(MessageNode)
        .filter(MessageNode.character_id == 523, MessageNode.role == "user")
        .one()
    )
    assert user_node.content == "hi"
    state = (
        db_session.query(AgentState)
        .filter(AgentState.character_id == 523)
        .first()
    )
    assert state.current_message_id == user_node.id


def test_delete_message_not_found_returns_404(client, db_session):
    resp = client.delete("/chat/message/999999")
    assert resp.status_code == 404
