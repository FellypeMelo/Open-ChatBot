"""Alembic migration guard.

Ensures the versioned migrations actually build the full current schema, so a
model change that ships without a matching migration is caught. Runs against a
throwaway temp database via `-x db_url=...` -- never the app's chatbot.db.
"""

import argparse
import os
import sqlite3
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config

from src.backend.db.database import Base
import src.backend.db.models  # noqa: F401 -- registers every table on Base.metadata

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _alembic_config(db_url: str) -> Config:
    cfg = Config(str(_REPO_ROOT / "alembic.ini"))
    # env.py reads the target DB from `-x db_url=...`; supply it via the API so
    # the migration never runs against the configured (real) database.
    cfg.cmd_opts = argparse.Namespace(x=[f"db_url={db_url}"])
    return cfg


def test_migrations_upgrade_head_builds_full_schema():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = "sqlite:///" + path.replace(os.sep, "/")
    try:
        command.upgrade(_alembic_config(url), "head")

        conn = sqlite3.connect(path)
        try:
            migrated = {
                row[0]
                for row in conn.execute(
                    "select name from sqlite_master where type='table'"
                )
            }
        finally:
            conn.close()

        expected = set(Base.metadata.tables.keys())
        missing = expected - migrated
        assert not missing, f"migration head is missing tables: {sorted(missing)}"
        assert "alembic_version" in migrated
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def test_migration_adds_parent_indexes_and_character_id_notnull():
    # Guards the 4856088c4fcd migration (ER review B3/B4): after upgrade head the
    # parent_id indexes exist and agent_states.character_id is NOT NULL.
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = "sqlite:///" + path.replace(os.sep, "/")
    try:
        command.upgrade(_alembic_config(url), "head")

        conn = sqlite3.connect(path)
        try:
            index_names = {
                row[1]
                for row in conn.execute("PRAGMA index_list('message_nodes')")
            }
            assert "ix_message_nodes_parent_id" in index_names
            assert "ix_message_nodes_parent_active" in index_names
            assert "ix_message_nodes_chat_active_ts" in index_names

            # PRAGMA table_info columns: (cid, name, type, notnull, dflt, pk).
            notnull = {
                row[1]: row[3]
                for row in conn.execute("PRAGMA table_info('agent_states')")
            }
            assert notnull["character_id"] == 1, "character_id must be NOT NULL"
        finally:
            conn.close()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
