from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
    # Migration: add lust column if not present (safe to run repeatedly)
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("characters")]
    if "lust" not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE characters ADD COLUMN lust INTEGER DEFAULT 0"))
            conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
