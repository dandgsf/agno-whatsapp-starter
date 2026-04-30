"""Small compatibility repairs for existing AgentOS databases."""

from __future__ import annotations

from agno.db.postgres import PostgresDb
from agno.utils.log import log_info, log_warning
from sqlalchemy import text


def _quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def ensure_approvals_run_status_column(db: PostgresDb) -> None:
    """Repair Agno 2.5.x approval tables for Agno 2.6+.

    Agno 2.6 validates `agno_approvals.run_status`. Existing Railway databases
    created before that column existed keep booting, but every run logs schema
    warnings and approval status updates fail. This migration is intentionally
    narrow and idempotent.
    """

    db_schema = db.db_schema or "ai"
    table_name = db.approvals_table_name
    full_table_name = f"{_quote_ident(db_schema)}.{_quote_ident(table_name)}"
    index_name = f"ix_{table_name}_run_status"

    with db.Session() as session, session.begin():
        table_exists = session.execute(
            text(
                "SELECT EXISTS ("
                "  SELECT FROM information_schema.tables"
                "  WHERE table_schema = :schema AND table_name = :table"
                ")"
            ),
            {"schema": db_schema, "table": table_name},
        ).scalar()
        if not table_exists:
            return

        column_exists = session.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_schema = :schema AND table_name = :table AND column_name = 'run_status'"
            ),
            {"schema": db_schema, "table": table_name},
        ).scalar()
        if column_exists:
            return

        log_info(f"Repairing {db_schema}.{table_name}: adding missing run_status column")
        session.execute(text(f"ALTER TABLE {full_table_name} ADD COLUMN run_status TEXT"))
        session.execute(
            text(f"CREATE INDEX IF NOT EXISTS {_quote_ident(index_name)} ON {full_table_name} (run_status)")
        )


def repair_agentos_db_schema(db: PostgresDb) -> None:
    """Run safe startup repairs for an existing AgentOS Postgres database."""

    try:
        ensure_approvals_run_status_column(db)
    except Exception as exc:  # noqa: BLE001
        log_warning(f"AgentOS database schema repair skipped: {exc}")
