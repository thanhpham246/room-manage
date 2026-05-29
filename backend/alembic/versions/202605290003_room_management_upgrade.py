"""Room management upgrade.

Revision ID: 202605290003
Revises: 202605290002
Create Date: 2026-05-29 16:40:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "202605290003"
down_revision: str | None = "202605290002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "rooms" not in inspect(op.get_bind()).get_table_names():
        return

    columns = table_columns("rooms")
    if "code" not in columns:
        op.add_column("rooms", sa.Column("code", sa.String(length=150), nullable=True))
    if "room_type" not in columns:
        op.add_column(
            "rooms",
            sa.Column(
                "room_type",
                sa.String(length=50),
                nullable=False,
                server_default="standard",
            ),
        )
    if "max_occupants" not in columns:
        op.add_column(
            "rooms",
            sa.Column("max_occupants", sa.Integer(), nullable=False, server_default="1"),
        )

    backfill_room_metadata()

    if "code" not in columns:
        op.alter_column("rooms", "code", nullable=False)
    if not has_index("rooms", "ix_rooms_code"):
        op.create_index("ix_rooms_code", "rooms", ["code"], unique=True)
    if not has_index("rooms", "ix_rooms_room_type"):
        op.create_index("ix_rooms_room_type", "rooms", ["room_type"])


def downgrade() -> None:
    if "rooms" not in inspect(op.get_bind()).get_table_names():
        return

    for index_name in ["ix_rooms_room_type", "ix_rooms_code"]:
        if has_index("rooms", index_name):
            op.drop_index(index_name, table_name="rooms")
    for column_name in ["max_occupants", "room_type", "code"]:
        if has_column("rooms", column_name):
            op.drop_column("rooms", column_name)


def backfill_room_metadata() -> None:
    op.execute(
        """
        UPDATE rooms
        SET code = buildings.code || '-' || rooms.name
        FROM buildings
        WHERE rooms.building_id = buildings.id
          AND (rooms.code IS NULL OR rooms.code = '')
        """
    )
    op.execute(
        """
        UPDATE rooms
        SET room_type = 'standard'
        WHERE room_type IS NULL OR room_type = ''
        """
    )
    op.execute(
        """
        UPDATE rooms
        SET max_occupants = 1
        WHERE max_occupants IS NULL OR max_occupants < 1
        """
    )


def table_columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def has_column(table_name: str, column_name: str) -> bool:
    return column_name in table_columns(table_name)


def has_index(table_name: str, index_name: str) -> bool:
    indexes = inspect(op.get_bind()).get_indexes(table_name)
    return any(index["name"] == index_name for index in indexes)
