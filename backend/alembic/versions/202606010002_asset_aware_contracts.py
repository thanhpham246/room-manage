"""Asset-aware contracts.

Revision ID: 202606010002
Revises: 202606010001
Create Date: 2026-06-01 10:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "202606010002"
down_revision: str | None = "202606010001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    table_names = inspect(bind).get_table_names()
    if "contracts" in table_names:
        upgrade_contracts(bind.dialect.name)
    if "invoices" in table_names:
        upgrade_invoices()


def downgrade() -> None:
    table_names = inspect(op.get_bind()).get_table_names()
    if "invoices" in table_names:
        downgrade_invoices()
    if "contracts" in table_names:
        downgrade_contracts()


def upgrade_contracts(dialect_name: str) -> None:
    columns = table_columns("contracts")
    additions = {
        "contract_code": sa.Column("contract_code", sa.String(length=50), nullable=True),
        "scope": sa.Column("scope", sa.String(length=32), nullable=False, server_default="room"),
        "building_id": sa.Column("building_id", sa.Integer(), nullable=True),
        "deleted_at": sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column("contracts", column)

    if "contract_code" not in columns:
        backfill_contract_codes(dialect_name)
        op.alter_column("contracts", "contract_code", nullable=False)
    if "building_id" not in columns:
        op.execute(
            """
            UPDATE contracts
            SET building_id = rooms.building_id
            FROM rooms
            WHERE contracts.room_id = rooms.id
              AND contracts.building_id IS NULL
            """
        )
        op.alter_column("contracts", "building_id", nullable=False)
        op.create_foreign_key(
            "fk_contracts_building_id_buildings",
            "contracts",
            "buildings",
            ["building_id"],
            ["id"],
        )
    if has_column("contracts", "room_id"):
        op.alter_column("contracts", "room_id", nullable=True)

    if not has_index("contracts", "ix_contracts_contract_code"):
        op.create_index(
            "ix_contracts_contract_code",
            "contracts",
            ["contract_code"],
            unique=True,
        )
    if not has_index("contracts", "ix_contracts_scope"):
        op.create_index("ix_contracts_scope", "contracts", ["scope"])
    if not has_index("contracts", "ix_contracts_building_id"):
        op.create_index("ix_contracts_building_id", "contracts", ["building_id"])
    if not has_index("contracts", "ix_contracts_deleted_at"):
        op.create_index("ix_contracts_deleted_at", "contracts", ["deleted_at"])


def upgrade_invoices() -> None:
    columns = table_columns("invoices")
    if "building_id" not in columns:
        op.add_column("invoices", sa.Column("building_id", sa.Integer(), nullable=True))
        op.execute(
            """
            UPDATE invoices
            SET building_id = rooms.building_id
            FROM rooms
            WHERE invoices.room_id = rooms.id
              AND invoices.building_id IS NULL
            """
        )
        op.execute(
            """
            UPDATE invoices
            SET building_id = contracts.building_id
            FROM contracts
            WHERE invoices.contract_id = contracts.id
              AND invoices.building_id IS NULL
            """
        )
        op.alter_column("invoices", "building_id", nullable=False)
        op.create_foreign_key(
            "fk_invoices_building_id_buildings",
            "invoices",
            "buildings",
            ["building_id"],
            ["id"],
        )
    if has_column("invoices", "room_id"):
        op.alter_column("invoices", "room_id", nullable=True)
    if not has_index("invoices", "ix_invoices_building_id"):
        op.create_index("ix_invoices_building_id", "invoices", ["building_id"])


def downgrade_contracts() -> None:
    for index_name in [
        "ix_contracts_deleted_at",
        "ix_contracts_building_id",
        "ix_contracts_scope",
        "ix_contracts_contract_code",
    ]:
        if has_index("contracts", index_name):
            op.drop_index(index_name, table_name="contracts")
    for column_name in ["deleted_at", "building_id", "scope", "contract_code"]:
        if has_column("contracts", column_name):
            op.drop_column("contracts", column_name)


def downgrade_invoices() -> None:
    if has_index("invoices", "ix_invoices_building_id"):
        op.drop_index("ix_invoices_building_id", table_name="invoices")
    if has_column("invoices", "building_id"):
        op.drop_column("invoices", "building_id")


def backfill_contract_codes(dialect_name: str) -> None:
    if dialect_name == "postgresql":
        op.execute(
            """
            UPDATE contracts
            SET contract_code = 'CONTRACT-' || lpad(id::text, 3, '0')
            WHERE contract_code IS NULL OR contract_code = ''
            """
        )
        return
    op.execute(
        """
        UPDATE contracts
        SET contract_code = 'CONTRACT-' || id
        WHERE contract_code IS NULL OR contract_code = ''
        """
    )


def table_columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def has_column(table_name: str, column_name: str) -> bool:
    return column_name in table_columns(table_name)


def has_index(table_name: str, index_name: str) -> bool:
    indexes = inspect(op.get_bind()).get_indexes(table_name)
    return any(index["name"] == index_name for index in indexes)
