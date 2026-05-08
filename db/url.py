"""
Database URL
------------

Build database connection URL from environment variables.
"""

from os import getenv
from urllib.parse import quote


def normalize_db_url(url: str) -> str:
    """Return a SQLAlchemy URL that uses the installed psycopg driver."""

    normalized = url.strip()
    if normalized.startswith("postgresql+psycopg://"):
        return normalized
    if normalized.startswith("postgresql://"):
        return normalized.replace("postgresql://", "postgresql+psycopg://", 1)
    if normalized.startswith("postgres://"):
        return normalized.replace("postgres://", "postgresql+psycopg://", 1)
    return normalized


def build_db_url() -> str:
    """Build database URL from environment variables."""
    database_url = getenv("DATABASE_URL")
    if database_url:
        return normalize_db_url(database_url)

    driver = getenv("DB_DRIVER", "postgresql+psycopg")
    user = getenv("DB_USER", "ai")
    password = quote(getenv("DB_PASS", "ai"), safe="")
    host = getenv("DB_HOST", "localhost")
    port = getenv("DB_PORT", "5432")
    database = getenv("DB_DATABASE", "ai")

    return f"{driver}://{user}:{password}@{host}:{port}/{database}"


db_url = build_db_url()
