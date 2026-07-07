from src.backend.db.models import MessageNode, Character, User


def test_message_node_branching(db_session):
    # 1. Setup - Create a character and user
    char = Character(name="Test Char", description="A test character")
    db_session.add(char)
    user = User(name="Test User")
    db_session.add(user)
    db_session.commit()

    # 2. Create Root Message (User)
    root = MessageNode(
        role="user",
        content="Hello!",
        type="speech",
        character_id=char.id,
        user_id=user.id,
    )
    db_session.add(root)
    db_session.commit()

    # 3. Create First Response (Assistant - Variant 0)
    resp1 = MessageNode(
        parent_id=root.id,
        role="assistant",
        content="Hi there!",
        type="speech",
        variant_index=0,
        character_id=char.id,
    )
    db_session.add(resp1)

    # 4. Create Second Response (Assistant - Variant 1 - Branching)
    resp2 = MessageNode(
        parent_id=root.id,
        role="assistant",
        content="Greetings!",
        type="speech",
        variant_index=1,
        character_id=char.id,
    )
    db_session.add(resp2)
    db_session.commit()

    # 5. Verify Branching
    db_session.refresh(root)
    assert len(root.children) == 2
    assert resp1 in root.children
    assert resp2 in root.children
    assert resp1.parent_id == root.id
    assert resp2.parent_id == root.id
    assert resp1.variant_index == 0
    assert resp2.variant_index == 1


def test_message_node_nested_tree(db_session):
    # Setup
    char = Character(name="Nested Char")
    db_session.add(char)
    db_session.commit()

    # Create a deeper tree
    # root -> child -> grandchild
    root = MessageNode(role="user", content="Root", character_id=char.id)
    db_session.add(root)
    db_session.commit()

    child = MessageNode(
        parent_id=root.id, role="assistant", content="Child", character_id=char.id
    )
    db_session.add(child)
    db_session.commit()

    grandchild = MessageNode(
        parent_id=child.id, role="user", content="Grandchild", character_id=char.id
    )
    db_session.add(grandchild)
    db_session.commit()

    # Verify
    db_session.refresh(root)
    db_session.refresh(child)

    assert len(root.children) == 1
    assert root.children[0].id == child.id
    assert len(child.children) == 1
    assert child.children[0].id == grandchild.id
    assert grandchild.parent.id == child.id
    assert child.parent.id == root.id
