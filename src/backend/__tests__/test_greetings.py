"""Alternate greetings: storage on the character card + seeding the opening
message when a new chat starts (with {{char}}/{{user}} macros resolved)."""


from src.backend.db.models import AgentState, MessageNode


def _make_char(client, **overrides):
    payload = {
        "name": "Aria",
        "description": "A calm librarian.",
        "first_mes": "Hello there, welcome.",
        "alternate_greetings": ["*The door creaks* Oh, {{user}}. It's you.", "A third opening."],
    }
    payload.update(overrides)
    resp = client.post("/characters/", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_create_and_get_persists_alternate_greetings(client):
    created = _make_char(client)
    assert created["alternate_greetings"] == [
        "*The door creaks* Oh, {{user}}. It's you.",
        "A third opening.",
    ]
    got = client.get(f"/characters/{created['id']}").json()
    assert got["alternate_greetings"][0].startswith("*The door creaks*")


def test_update_replaces_alternate_greetings(client):
    created = _make_char(client)
    resp = client.put(
        f"/characters/{created['id']}",
        json={
            "name": "Aria",
            "description": "A calm librarian.",
            "first_mes": "Hi.",
            "alternate_greetings": ["only one alt now"],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["alternate_greetings"] == ["only one alt now"]


def test_new_chat_seeds_default_first_greeting(client, db_session):
    created = _make_char(client)
    cid = created["id"]

    resp = client.post(f"/chat/new/{cid}")
    assert resp.status_code == 200
    chat_id = resp.json()["chat_id"]

    msgs = (
        db_session.query(MessageNode)
        .filter(MessageNode.chat_id == chat_id)
        .all()
    )
    assert len(msgs) == 1
    assert msgs[0].role == "assistant"
    assert msgs[0].content == "Hello there, welcome."  # first_mes by default
    # It becomes the chat's opening pointer.
    state = db_session.query(AgentState).filter(AgentState.character_id == cid).first()
    assert state.current_message_id == msgs[0].id


def test_new_chat_seeds_chosen_greeting_with_macros_resolved(client, db_session):
    created = _make_char(client)
    cid = created["id"]

    # Choose alternate greeting index 1 (the {{user}} one). Active user name is
    # "User" (get_or_create_active default) -> macro resolves.
    resp = client.post(f"/chat/new/{cid}", json={"greeting_index": 1})
    assert resp.status_code == 200
    chat_id = resp.json()["chat_id"]

    msg = (
        db_session.query(MessageNode)
        .filter(MessageNode.chat_id == chat_id)
        .first()
    )
    assert msg is not None
    assert "{{user}}" not in msg.content
    assert "Oh, User. It's you." in msg.content


def test_new_chat_without_greetings_seeds_nothing(client, db_session):
    resp = client.post(
        "/characters/",
        json={"name": "Blank", "description": "d", "first_mes": "", "alternate_greetings": []},
    )
    cid = resp.json()["id"]
    chat_id = client.post(f"/chat/new/{cid}").json()["chat_id"]
    msgs = db_session.query(MessageNode).filter(MessageNode.chat_id == chat_id).all()
    assert msgs == []
