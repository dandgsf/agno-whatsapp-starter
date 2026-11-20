"""
Database URL
------------

Build database connection URL from environment variables.
"""

from urllib.parse import quote

from utils.validate_envs import DatabaseSettings


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
    settings = DatabaseSettings()
    if settings.database_url.strip():
        return normalize_db_url(settings.database_url)

    user = quote(settings.db_user, safe="")
    password = quote(settings.db_pass, safe="")
    return f"{settings.db_driver}://{user}:{password}@{settings.db_host}:{settings.db_port}/{settings.db_database}"


db_url = build_db_url()
