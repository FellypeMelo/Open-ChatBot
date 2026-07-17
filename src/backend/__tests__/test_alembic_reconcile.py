"""B1: init_db must reconcile the create_all/ALTER-built schema with Alembic by
stamping an untracked DB to head (so a later `alembic upgrade head` starts from
head instead of colliding with existing tables), without ever auto-upgrading or
touching an already-tracked DB. All isolated against a temp SQLite file.
"""

from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from src.backend.core.config import settings
from src.backend.db.database import (
    Base,
    _alembic_config,
    stamp_alembic_head_if_untracked,
)


def _head_revision() -> str:
    return ScriptDirectory.from_config(_alembic_config()).get_current_head()


def _build_schema(url: str) -> None:
    eng = create_engine(url)
    import src.backend.db.models  # noqa: F401 -- register tables on Base.metadata

    Base.metadata.create_all(eng)
    eng.dispose()


def test_stamp_marks_untracked_db_at_head(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 't.db'}"
    monkeypatch.setattr(settings, "TESTING", False)
    monkeypatch.setattr(settings, "DATABASE_URL", url)

    _build_schema(url)  # create_all-born DB: no alembic_version yet

    eng = create_engine(url)
    assert "alembic_version" not in inspect(eng).get_table_names()
    eng.dispose()

    stamp_alembic_head_if_untracked()

    eng = create_engine(url)
    assert "alembic_version" in inspect(eng).get_table_names()
    with eng.connect() as conn:
        ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    eng.dispose()
    assert ver == _head_revision()


def test_stamp_leaves_already_tracked_db_untouched(tmp_path, monkeypatch):
    # A DB already carrying an alembic_version at a NON-head revision must be
    # left alone -- catching it up is the user's `alembic upgrade head`, not ours.
    url = f"sqlite:///{tmp_path / 't2.db'}"
    monkeypatch.setattr(settings, "TESTING", False)
    monkeypatch.setattr(settings, "DATABASE_URL", url)

    _build_schema(url)
    stamp_alembic_head_if_untracked()  # first: stamps head

    base_rev = ScriptDirectory.from_config(_alembic_config()).get_base()
    eng = create_engine(url)
    with eng.begin() as conn:
        conn.execute(
            text("UPDATE alembic_version SET version_num = :r"), {"r": base_rev}
        )
    eng.dispose()

    stamp_alembic_head_if_untracked()  # second: sees a version -> no-op

    eng = create_engine(url)
    with eng.connect() as conn:
        ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    eng.dispose()
    assert ver == base_rev  # untouched


def test_stamp_is_a_noop_under_testing(monkeypatch):
    # settings.TESTING must short-circuit so a test run never stamps a real DB.
    monkeypatch.setattr(settings, "TESTING", True)
    # Must return without importing alembic.command / connecting anywhere.
    stamp_alembic_head_if_untracked()


def test_wal_and_fk_pragmas_applied_on_file_db(tmp_path):
    # PF: a file-backed connection gets WAL + FK enforcement (the one perf win
    # from the analysis). WAL is unsupported on :memory:, so test a file DB.
    import sqlite3
    from src.backend.db.database import _apply_sqlite_pragmas

    conn = sqlite3.connect(str(tmp_path / "wal.db"))
    try:
        _apply_sqlite_pragmas(conn)
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    finally:
        conn.close()
    assert mode.lower() == "wal"
    assert fk == 1
