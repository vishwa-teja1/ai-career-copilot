"""
SQLAlchemy engine + session factory.
A single source of truth for DB connectivity, used by the DI providers
in api/deps.py so repositories/services never construct sessions themselves.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping avoids "server closed the connection unexpectedly" errors
# after long idle periods (common with managed Postgres like RDS).
# pool_size/max_overflow only apply to QueuePool-based backends (Postgres) -
# SQLite (used for local unit tests) uses a different default pool and
# rejects those kwargs, so they're added conditionally.
_engine_kwargs = {"pool_pre_ping": True, "future": True}
if not settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update(pool_size=10, max_overflow=20)

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a DB session and guarantees it's closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
