"""Add trigram search indexes.

Revision ID: 202605300001
Revises: 202605290003
Create Date: 2026-05-30 20:30:00
"""

from collections.abc import Sequence

from sqlalchemy import inspect

from alembic import op

revision: str = "202605300001"
down_revision: str | None = "202605290003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    table_names = inspect(bind).get_table_names()

    if "buildings" in table_names:
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_buildings_search_trgm
            ON buildings
            USING GIN (
                (
                    lower(
                        coalesce(code, '')
                        || ' '
                        || coalesce(name, '')
                        || ' '
                        || coalesce(address, '')
                    )
                ) gin_trgm_ops
            )
            """
        )

    if "rooms" in table_names:
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_rooms_search_trgm
            ON rooms
            USING GIN (
                (
                    lower(
                        coalesce(code, '')
                        || ' '
                        || coalesce(name, '')
                    )
                ) gin_trgm_ops
            )
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("DROP INDEX IF EXISTS ix_rooms_search_trgm")
    op.execute("DROP INDEX IF EXISTS ix_buildings_search_trgm")
