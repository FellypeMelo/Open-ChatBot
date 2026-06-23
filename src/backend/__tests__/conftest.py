import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.db.database import Base, get_db
from src.backend.main import app

# Global Testing Isolation Ruleset Enforcement
@pytest.fixture(scope="session")
def test_db_setup():
    """
    Creates a temporary isolated SQLite database for the duration of the test session.
    """
    db_fd, db_path = tempfile.mkstemp()
    test_db_url = f"sqlite:///{db_path}"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    
    # Create all tables in the isolated DB
    Base.metadata.create_all(bind=engine)
    
    # Provide the engine to tests
    yield engine
    
    # Cleanup after session
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
        
    os.close(db_fd)
    
    # Use a small delay or try/except to handle Windows file locking
    import time
    max_retries = 3
    for i in range(max_retries):
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
            break
        except PermissionError:
            if i < max_retries - 1:
                time.sleep(0.1)
            else:
                print(f"Warning: Could not delete temporary database {db_path}")

@pytest.fixture
def db_session(test_db_setup):
    """
    Provides a clean database session for each test, ensuring atomicity via transactions.
    """
    connection = test_db_setup.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """
    Provides a FastAPI test client with the database dependency overridden to use the isolated test DB.
    """
    from fastapi.testclient import TestClient
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_vector_store_path(tmp_path, monkeypatch):
    """
    Automatically mock/redirect the vector store path to a temporary folder
    for ALL tests to guarantee Mandatory Environment Isolation.
    """
    from src.backend.api import chat
    from src.backend.core.memory.vector_store import VectorStore
    
    # Create a temporary VectorStore instance for the chat router
    test_vs = VectorStore(llm_client=chat.llama, path=str(tmp_path / "test_chroma_db"))
    monkeypatch.setattr(chat, "vector_store", test_vs)
