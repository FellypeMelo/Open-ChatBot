from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from src.backend.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
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
