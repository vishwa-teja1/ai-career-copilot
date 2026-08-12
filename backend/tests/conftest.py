import os
import uuid

os.environ.setdefault("SECRET_KEY", "test_secret_key_do_not_use_in_production")
os.environ.setdefault("FIELD_ENCRYPTION_KEY", "sFVaXsbmi-D2MbO3FC_kDsby-V7K8VH_9M9bfRu1cEw=")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
# The TestClient always hits the API from the same "IP", so the production
# per-IP auth rate limit would throttle the test suite itself - raise it here.
os.environ.setdefault("RATE_LIMIT_AUTH", "10000/minute")
os.environ.setdefault("RATE_LIMIT_DEFAULT", "10000/minute")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# NOTE: production uses Postgres-specific types (UUID, ARRAY). For fast,
# dependency-free unit tests we exercise the service/repository layer
# against SQLite here; full-type integration tests should run against a
# real Postgres instance in CI (see docker-compose.test.yml).
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"
