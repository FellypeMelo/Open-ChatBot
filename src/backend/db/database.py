from pathlib import Path

from sqlalchemy import create_engine, text, inspect, event
from sqlalchemy.orm import sessionmaker, declarative_base
from src.backend.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _apply_sqlite_pragmas(dbapi_connection):
    """Per-connection SQLite pragmas:
    - foreign_keys=ON: SQLite ships FK enforcement OFF, so ondelete=CASCADE never
      fired and deleting a character/chat orphaned its messages/journals/lore.
    - journal_mode=WAL + synchronous=NORMAL: the default rollback journal fsyncs
      and takes an exclusive lock on every COMMIT, and a normal turn commits 3+
      times while the background reflection commits concurrently -- under a
      rollback journal that background writer also blocks the next turn's reads.
      WAL lets the single writer and readers proceed without blocking each other
      and makes each commit far cheaper, while staying fully durable. NORMAL only
      risks the last committed transaction on an OS-level power loss -- acceptable
      for a local app and no weaker than the vector store's own durability.
      (No-op / stays 'memory' on in-memory test DBs, which don't support WAL.)"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


@event.listens_for(engine, "connect")
def _configure_sqlite_connection(dbapi_connection, connection_record):
    # Endpoints also clean up explicitly, so isolated test engines without this
    # listener stay correct.
    try:
        _apply_sqlite_pragmas(dbapi_connection)
    except Exception:
        pass


def init_db():
    # First-run / test convenience: create_all builds the current schema directly.
    # Schema *evolution* on an existing database is owned by Alembic
    # (src/backend/db/migrations); run `alembic upgrade head`. The ad-hoc
    # ALTER TABLE blocks below remain only to carry pre-Alembic databases forward.
    import src.backend.db.models  # noqa: F401 -- registers all models on Base.metadata before create_all()

    Base.metadata.create_all(bind=engine)

    # Safely add missing columns for schema updates
    insp = inspect(engine)
    with engine.begin() as conn:
        if "message_nodes" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("message_nodes")]
            if "is_active" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE message_nodes ADD COLUMN is_active BOOLEAN DEFAULT 1"
                    )
                )

        if "agent_states" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("agent_states")]
            if "active_summary" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE agent_states ADD COLUMN active_summary TEXT DEFAULT ''"
                    )
                )
            if "location" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE agent_states ADD COLUMN location TEXT DEFAULT 'Living Room'"
                    )
                )
            if "mood" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE agent_states ADD COLUMN mood TEXT DEFAULT 'Neutral'"
                    )
                )
            if "clothes" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE agent_states ADD COLUMN clothes TEXT DEFAULT 'Casual'"
                    )
                )
            if "version" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE agent_states ADD COLUMN version INTEGER DEFAULT 1"
                    )
                )
            if "last_reflected_at_count" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE agent_states ADD COLUMN last_reflected_at_count INTEGER DEFAULT 0"
                    )
                )

        if "chats" in insp.get_table_names():
            chat_cols = [col["name"] for col in insp.get_columns("chats")]
            if "last_reflected_at_count" not in chat_cols:
                conn.execute(
                    text(
                        "ALTER TABLE chats ADD COLUMN last_reflected_at_count INTEGER DEFAULT 0"
                    )
                )
            # B8 (independent storylines): per-chat persona snapshot columns.
            if "location" not in chat_cols:
                conn.execute(
                    text("ALTER TABLE chats ADD COLUMN location TEXT DEFAULT 'Living Room'")
                )
            if "mood" not in chat_cols:
                conn.execute(
                    text("ALTER TABLE chats ADD COLUMN mood TEXT DEFAULT 'Neutral'")
                )
            if "clothes" not in chat_cols:
                conn.execute(
                    text("ALTER TABLE chats ADD COLUMN clothes TEXT DEFAULT 'Casual'")
                )
            if "stats" not in chat_cols:
                conn.execute(text("ALTER TABLE chats ADD COLUMN stats TEXT"))
                # One-time backfill: copy each character's current global persona
                # into ALL its existing chats, so splitting the shared persona into
                # per-chat storylines loses no accumulated relationship/mood (B8).
                conn.execute(
                    text(
                        "UPDATE chats SET "
                        "location = COALESCE((SELECT location FROM agent_states s WHERE s.character_id = chats.character_id), 'Living Room'), "
                        "mood = COALESCE((SELECT mood FROM agent_states s WHERE s.character_id = chats.character_id), 'Neutral'), "
                        "clothes = COALESCE((SELECT clothes FROM agent_states s WHERE s.character_id = chats.character_id), 'Casual'), "
                        "stats = (SELECT stats FROM agent_states s WHERE s.character_id = chats.character_id)"
                    )
                )

        if "users" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("users")]
            if "persona_description" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN persona_description TEXT DEFAULT ''"
                    )
                )
            if "appearance" not in columns:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN appearance TEXT DEFAULT ''")
                )
            if "gender" not in columns:
                conn.execute(
                    text("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT ''")
                )

        if "characters" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("characters")]
            if "short_description" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN short_description TEXT DEFAULT ''"
                    )
                )
            if "persona_prompt" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN persona_prompt TEXT DEFAULT ''"
                    )
                )
            if "nickname" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN nickname TEXT DEFAULT ''"
                    )
                )
            if "scenario" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN scenario TEXT DEFAULT ''"
                    )
                )
            if "first_mes" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN first_mes TEXT DEFAULT ''"
                    )
                )
            if "mes_example" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN mes_example TEXT DEFAULT ''"
                    )
                )
            if "alternate_greetings" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN alternate_greetings TEXT DEFAULT '[]'"
                    )
                )
            if "content_rating" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE characters ADD COLUMN content_rating TEXT DEFAULT 'limited'"
                    )
                )

        # Lorebook V2 fields: the table predates the advanced-scanner columns
        # (keys, probability, insertion_order, ...). create_all() never ALTERs
        # an existing table, so a DB created before these columns crashes every
        # chat turn (lorebook_scanner SELECTs them). Backfill idempotently.
        if "lorebook_entries" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("lorebook_entries")]
            lorebook_additions = [
                ("keys", "TEXT DEFAULT '[]'"),
                ("secondary_keys", "TEXT DEFAULT '[]'"),
                ("insertion_order", "INTEGER DEFAULT 100"),
                ("probability", "INTEGER DEFAULT 100"),
                ("scan_depth", "INTEGER DEFAULT 5"),
                ("is_constant", "BOOLEAN DEFAULT 0"),
                ("cooldown_turns", "INTEGER DEFAULT 0"),
            ]
            for col_name, col_def in lorebook_additions:
                if col_name not in columns:
                    conn.execute(
                        text(
                            f"ALTER TABLE lorebook_entries ADD COLUMN {col_name} {col_def}"
                        )
                    )

        # Chat/Session scoping (per-chat memory isolation). create_all() makes
        # the new `chats` table but never ALTERs the existing message/journal/
        # agent_state tables, so add their scoping columns idempotently.
        if "message_nodes" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("message_nodes")]
            if "chat_id" not in columns:
                conn.execute(
                    text("ALTER TABLE message_nodes ADD COLUMN chat_id INTEGER")
                )
        if "journal_entries" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("journal_entries")]
            if "chat_id" not in columns:
                conn.execute(
                    text("ALTER TABLE journal_entries ADD COLUMN chat_id INTEGER")
                )
        if "agent_states" in insp.get_table_names():
            columns = [col["name"] for col in insp.get_columns("agent_states")]
            if "active_chat_id" not in columns:
                conn.execute(
                    text("ALTER TABLE agent_states ADD COLUMN active_chat_id INTEGER")
                )

        # Backfill: give every pre-existing conversation a Chat row so its
        # history/journal become chat-scoped and the character gets an active
        # chat pointer. Idempotent -- only touches rows still lacking a chat_id.
        if (
            "chats" in insp.get_table_names()
            and "message_nodes" in insp.get_table_names()
        ):
            orphan_char_ids = conn.execute(
                text(
                    "SELECT DISTINCT character_id FROM message_nodes "
                    "WHERE chat_id IS NULL AND character_id IS NOT NULL"
                )
            ).fetchall()
            for (cid,) in orphan_char_ids:
                res = conn.execute(
                    text(
                        "INSERT INTO chats "
                        "(character_id, title, is_archived, active_summary, interaction_count) "
                        "VALUES (:cid, 'Imported Chat', 0, '', 0)"
                    ),
                    {"cid": cid},
                )
                new_chat_id = res.lastrowid
                conn.execute(
                    text(
                        "UPDATE message_nodes SET chat_id = :chat "
                        "WHERE character_id = :cid AND chat_id IS NULL"
                    ),
                    {"chat": new_chat_id, "cid": cid},
                )
                conn.execute(
                    text(
                        "UPDATE journal_entries SET chat_id = :chat "
                        "WHERE character_id = :cid AND chat_id IS NULL"
                    ),
                    {"chat": new_chat_id, "cid": cid},
                )
                # Point the character's AgentState at the imported chat and copy
                # its conversation-local snapshot (pointer/summary/counter).
                conn.execute(
                    text(
                        "UPDATE chats SET "
                        "current_message_id = (SELECT current_message_id FROM agent_states WHERE character_id = :cid), "
                        "active_summary = COALESCE((SELECT active_summary FROM agent_states WHERE character_id = :cid), ''), "
                        "interaction_count = COALESCE((SELECT interaction_count FROM agent_states WHERE character_id = :cid), 0) "
                        "WHERE id = :chat"
                    ),
                    {"cid": cid, "chat": new_chat_id},
                )
                conn.execute(
                    text(
                        "UPDATE agent_states SET active_chat_id = :chat "
                        "WHERE character_id = :cid AND active_chat_id IS NULL"
                    ),
                    {"chat": new_chat_id, "cid": cid},
                )

    # The schema is now fully built (create_all + ALTER compat). Record it as
    # Alembic head so a future `alembic upgrade head` reconciles instead of
    # colliding with the existing tables (B1). Never auto-upgrades.
    stamp_alembic_head_if_untracked()


def _alembic_config():
    """Alembic Config pointing at the repo's alembic.ini (script_location +
    env.py, which resolves the DB URL from settings.DATABASE_URL)."""
    from alembic.config import Config

    ini_path = Path(__file__).resolve().parents[3] / "alembic.ini"
    return Config(str(ini_path))


def stamp_alembic_head_if_untracked():
    """Reconcile the two schema-management systems (B1).

    First-run/carry-forward builds the schema via create_all + the ALTER compat
    blocks in init_db, so a fresh or pre-Alembic DB ends up at HEAD *schema* but
    with no `alembic_version` row. A later `alembic upgrade head` (run by the
    user -- we never auto-upgrade) would then start from the base revision and
    try to CREATE TABLE on already-existing tables and fail.

    Fix: once the schema is at head, STAMP the DB to head when it isn't tracked
    yet. Stamping records the version without touching the schema, so it can
    never skip a real migration -- the ALTER compat has already applied every
    column head expects. Idempotent: a DB already carrying an alembic_version is
    left untouched (a real pending migration is then the user's `upgrade head`)."""
    if settings.TESTING:
        return
    from alembic import command

    probe = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    try:
        insp = inspect(probe)
        if "alembic_version" in insp.get_table_names():
            with probe.connect() as conn:
                already = conn.execute(
                    text("SELECT version_num FROM alembic_version LIMIT 1")
                ).first()
            if already:
                return
    finally:
        probe.dispose()

    command.stamp(_alembic_config(), "head")


def seed_default_presets():
    """Guarantee at least one SamplerPreset (with is_default=True) exists from
    app startup -- not lazily on first GET /presets -- so llm.py's
    Settings.TEMPERATURE-etc fallback (used only when no preset row exists at
    all) stays a true last-resort, not something that depends on request
    ordering. Called from main.py's lifespan (gated behind is_testing, same as
    init_db/vacuum_db) rather than from init_db() itself, since it needs a
    real SessionLocal() and must never run against a test's mocked engine."""
    from src.backend.db.models import SamplerPreset

    db = SessionLocal()
    try:
        if db.query(SamplerPreset).count() > 0:
            return
        db.add(
            SamplerPreset(
                name="Creative",
                is_default=True,
                temperature=1.05,
                min_p=0.03,
                top_k=0,
                top_p=1.0,
                repeat_penalty=1.0,
                dry_multiplier=0.8,
                dry_base=1.75,
                dry_range=4096,
                xtc_threshold=0.1,
                xtc_probability=0.4,
            )
        )
        db.add(
            SamplerPreset(
                name="Focused",
                is_default=False,
                temperature=0.7,
                min_p=0.05,
                top_k=0,
                top_p=1.0,
                repeat_penalty=1.0,
                dry_multiplier=0.6,
                dry_base=1.75,
                dry_range=2048,
                xtc_threshold=0.0,
                xtc_probability=0.0,
            )
        )
        db.commit()
    finally:
        db.close()


def vacuum_db():
    try:
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(text("VACUUM"))
    except Exception:
        # Non-critical on startup
        pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
