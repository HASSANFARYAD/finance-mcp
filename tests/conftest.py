import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ensure project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app
from app.db import session as db_session
from app.models.base import Base
# import models to register with Base.metadata
from app import models  # noqa: F401


@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    db = SessionLocal()

    # override dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[db_session.get_db] = override_get_db

    yield db

    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):  # noqa: F811 - uses db fixture to ensure DB is ready
    return TestClient(app)
