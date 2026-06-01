"""Tenant management upgrade.

Revision ID: 202606010001
Revises: 202605300001
Create Date: 2026-06-01 09:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "202606010001"
down_revision: str | None = "202605300001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if "tenants" not in inspect(bind).get_table_names():
        return

    columns = table_columns("tenants")
    additions = {
        "tenant_code": sa.Column("tenant_code", sa.String(length=50), nullable=True),
        "zalo": sa.Column("zalo", sa.String(length=100), nullable=True),
        "date_of_birth": sa.Column("date_of_birth", sa.Date(), nullable=True),
        "gender": sa.Column("gender", sa.String(length=32), nullable=True),
        "identity_type": sa.Column("identity_type", sa.String(length=32), nullable=True),
        "identity_issued_date": sa.Column("identity_issued_date", sa.Date(), nullable=True),
        "identity_issued_place": sa.Column(
            "identity_issued_place",
            sa.String(length=255),
            nullable=True,
        ),
        "permanent_address": sa.Column("permanent_address", sa.String(length=500), nullable=True),
        "current_address": sa.Column("current_address", sa.String(length=500), nullable=True),
        "emergency_contact_name": sa.Column(
            "emergency_contact_name",
            sa.String(length=255),
            nullable=True,
        ),
        "emergency_contact_phone": sa.Column(
            "emergency_contact_phone",
            sa.String(length=50),
            nullable=True,
        ),
        "emergency_contact_relationship": sa.Column(
            "emergency_contact_relationship",
            sa.String(length=100),
            nullable=True,
        ),
        "note": sa.Column("note", sa.Text(), nullable=True),
        "deleted_at": sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column("tenants", column)

    if "tenant_code" not in columns:
        backfill_tenant_codes(bind.dialect.name)
        op.alter_column("tenants", "tenant_code", nullable=False)
    if "emergency_contact" in columns and "emergency_contact_phone" not in columns:
        op.execute(
            """
            UPDATE tenants
            SET emergency_contact_phone = emergency_contact
            WHERE emergency_contact_phone IS NULL
              AND emergency_contact IS NOT NULL
            """
        )

    if not has_index("tenants", "ix_tenants_tenant_code"):
        op.create_index("ix_tenants_tenant_code", "tenants", ["tenant_code"], unique=True)
    if not has_index("tenants", "ix_tenants_deleted_at"):
        op.create_index("ix_tenants_deleted_at", "tenants", ["deleted_at"])

    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_tenants_identity_number_active
            ON tenants (identity_number)
            WHERE identity_number IS NOT NULL AND deleted_at IS NULL
            """
        )
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_tenants_search_trgm
            ON tenants
            USING GIN (
                (
                    lower(
                        coalesce(tenant_code, '')
                        || ' '
                        || coalesce(full_name, '')
                        || ' '
                        || coalesce(phone, '')
                        || ' '
                        || coalesce(email, '')
                        || ' '
                        || coalesce(identity_number, '')
                    )
                ) gin_trgm_ops
            )
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if "tenants" not in inspect(bind).get_table_names():
        return

    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_tenants_search_trgm")
        op.execute("DROP INDEX IF EXISTS uq_tenants_identity_number_active")
    for index_name in ["ix_tenants_deleted_at", "ix_tenants_tenant_code"]:
        if has_index("tenants", index_name):
            op.drop_index(index_name, table_name="tenants")
    for column_name in [
        "deleted_at",
        "note",
        "emergency_contact_relationship",
        "emergency_contact_phone",
        "emergency_contact_name",
        "current_address",
        "permanent_address",
        "identity_issued_place",
        "identity_issued_date",
        "identity_type",
        "gender",
        "date_of_birth",
        "zalo",
        "tenant_code",
    ]:
        if has_column("tenants", column_name):
            op.drop_column("tenants", column_name)


def backfill_tenant_codes(dialect_name: str) -> None:
    if dialect_name == "postgresql":
        op.execute(
            """
            UPDATE tenants
            SET tenant_code = 'TENANT-' || lpad(id::text, 3, '0')
            WHERE tenant_code IS NULL OR tenant_code = ''
            """
        )
        return
    op.execute(
        """
        UPDATE tenants
        SET tenant_code = 'TENANT-' || id
        WHERE tenant_code IS NULL OR tenant_code = ''
        """
    )


def table_columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def has_column(table_name: str, column_name: str) -> bool:
    return column_name in table_columns(table_name)


def has_index(table_name: str, index_name: str) -> bool:
    indexes = inspect(op.get_bind()).get_indexes(table_name)
    return any(index["name"] == index_name for index in indexes)
