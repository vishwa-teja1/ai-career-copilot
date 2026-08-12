"""
Cross-dialect column types.

Production always runs on Postgres, where we want native UUID and ARRAY
columns for proper indexing/typing. Unit tests run against in-memory SQLite
for speed, which has neither type. These TypeDecorators use the native
Postgres type when available and fall back to a CHAR(36)/JSON-encoded
representation otherwise, so the exact same model file works in both.
"""
import json
import uuid

from sqlalchemy import CHAR, TypeDecorator, Text
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        return str(value) if isinstance(value, uuid.UUID) else str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class StringArray(TypeDecorator):
    """list[str] column - native ARRAY(String) on Postgres, JSON-encoded TEXT elsewhere."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(Text()))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return json.loads(value)
