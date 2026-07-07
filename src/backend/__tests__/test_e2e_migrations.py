import os
import sqlite3
import tempfile
from sqlalchemy import create_engine, text, inspect
from unittest.mock import patch
from src.backend.db.database import init_db


def test_e2e_database_migration():
    """
    E2E Test to ensure that when an old version of the physical SQLite database exists,
    our manual migration logic in init_db() correctly runs ALTER TABLE and injects
    missing columns (active_summary, persona_description, etc) without data loss.
    """
    # 1. Setup a temporary physical DB file (simulating old production DB)
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "old_chatbot.db")

    # 2. Create old schema without the new columns using raw sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Old users table (missing persona_description, appearance, gender)
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            is_active BOOLEAN
        )
    """)
    # Old agent_states table (missing active_summary, location, mood, clothes)
    cursor.execute("""
        CREATE TABLE agent_states (
            id INTEGER PRIMARY KEY,
            character_id INTEGER,
            interaction_count INTEGER
        )
    """)
    # Old characters table (missing short_description, persona_prompt)
    cursor.execute("""
        CREATE TABLE characters (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    """)

    # Insert some dummy data to ensure it doesn't get wiped out by the migration
    cursor.execute(
        "INSERT INTO users (id, name, is_active) VALUES (1, 'LegacyUser', 1)"
    )
    conn.commit()
    conn.close()

    # 3. Patch the global engine in database.py to point to our persistent temp DB
    test_db_url = f"sqlite:///{db_path}"
    test_engine = create_engine(test_db_url)

    with patch("src.backend.db.database.engine", test_engine):
        # 4. Trigger our init_db() - this should detect missing columns and run ALTER TABLE
        init_db()

        # 5. Verify the schema actually got migrated!
        insp = inspect(test_engine)

        # Check users table
        user_columns = [col["name"] for col in insp.get_columns("users")]
        assert "persona_description" in user_columns, (
            "Migration failed: persona_description missing"
        )
        assert "appearance" in user_columns, "Migration failed: appearance missing"
        assert "gender" in user_columns, "Migration failed: gender missing"

        # Check agent_states table
        agent_columns = [col["name"] for col in insp.get_columns("agent_states")]
        assert "active_summary" in agent_columns, (
            "Migration failed: active_summary missing"
        )
        assert "location" in agent_columns, "Migration failed: location missing"

        # Check characters table
        char_columns = [col["name"] for col in insp.get_columns("characters")]
        assert "short_description" in char_columns, (
            "Migration failed: short_description missing"
        )
        assert "persona_prompt" in char_columns, (
            "Migration failed: persona_prompt missing"
        )

        # 6. Verify legacy data was preserved and we can write to the new columns using raw SQL
        with test_engine.begin() as db_conn:
            # Check legacy data
            legacy_user = db_conn.execute(
                text("SELECT name FROM users WHERE id=1")
            ).scalar()
            assert legacy_user == "LegacyUser", "Data loss during migration!"

            # Write to new column
            db_conn.execute(
                text(
                    "UPDATE users SET persona_description = 'Updated Persona' WHERE id=1"
                )
            )
            updated_desc = db_conn.execute(
                text("SELECT persona_description FROM users WHERE id=1")
            ).scalar()
            assert updated_desc == "Updated Persona"

    # Cleanup temp file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass
