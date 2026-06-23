from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from src.backend.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import src.backend.db.models
    Base.metadata.create_all(bind=engine)

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
