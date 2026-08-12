"""
Quick local smoke-test helper: creates all tables directly from the
SQLAlchemy models, bypassing Alembic.

Why this exists: the checked-in Alembic migration (alembic/versions/0001_*.py)
intentionally uses native Postgres types (UUID, ARRAY) since that's what
production runs on - which means `alembic upgrade head` will fail against
SQLite. For real development, point DATABASE_URL at Postgres and use Alembic
normally. This script is only for a zero-dependency local smoke test, e.g.
DATABASE_URL=sqlite:///./dev.db, where the portable GUID/StringArray types
in app/core/db_types.py degrade gracefully.

Usage:
    DATABASE_URL=sqlite:///./dev.db python scripts/create_dev_db.py
"""
import os
import sys

# Allows `python scripts/create_dev_db.py` to work regardless of cwd, since
# Python only auto-adds the script's own directory (scripts/) to sys.path,
# not the backend/ project root where the `app` package lives.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403 - registers all models on Base.metadata

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print(f"Created tables: {sorted(Base.metadata.tables.keys())}")
