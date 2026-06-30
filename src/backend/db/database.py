from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from src.backend.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    import src.backend.db.models

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
