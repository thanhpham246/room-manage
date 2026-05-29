"""House management upgrade.

Revision ID: 202605290002
Revises: 202605290001
Create Date: 2026-05-29 14:55:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "202605290002"
down_revision: str | None = "202605290001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    table_names = inspect(bind).get_table_names()

    if "buildings" in table_names:
        add_building_columns()
    if "floors" not in table_names:
        create_floors_table()
    if "building_amenities" not in table_names:
        create_building_amenities_table()
    if "building_expense_templates" not in table_names:
        create_building_expense_templates_table()
    if "rooms" in table_names:
        add_room_floor_id()
        backfill_floors_and_room_links()


def downgrade() -> None:
    bind = op.get_bind()
    table_names = inspect(bind).get_table_names()
    if "building_expense_templates" in table_names:
        op.drop_table("building_expense_templates")
    if "building_amenities" in table_names:
        op.drop_table("building_amenities")
    if "rooms" in table_names and has_column("rooms", "floor_id"):
        op.drop_index("ix_rooms_floor_id", table_name="rooms")
        op.drop_column("rooms", "floor_id")
    if "floors" in table_names:
        op.drop_table("floors")
    if "buildings" in table_names:
        drop_building_columns()


def add_building_columns() -> None:
    columns = table_columns("buildings")
    additions = {
        "code": sa.Column("code", sa.String(length=50), nullable=True),
        "house_type": sa.Column(
            "house_type",
            sa.String(length=50),
            nullable=False,
            server_default="boarding_house",
        ),
        "number_of_floors": sa.Column(
            "number_of_floors",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        "owner_name": sa.Column("owner_name", sa.String(length=255), nullable=True),
        "owner_phone": sa.Column("owner_phone", sa.String(length=50), nullable=True),
        "owner_email": sa.Column("owner_email", sa.String(length=255), nullable=True),
        "manager_id": sa.Column("manager_id", sa.Integer(), nullable=True),
        "status": sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="active",
        ),
        "phone": sa.Column("phone", sa.String(length=50), nullable=True),
        "email": sa.Column("email", sa.String(length=255), nullable=True),
        "zalo": sa.Column("zalo", sa.String(length=100), nullable=True),
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
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column("buildings", column)
    if "code" not in columns:
        op.execute(
            """
            UPDATE buildings
            SET code = 'HOUSE-' || lpad(id::text, 3, '0')
            WHERE code IS NULL OR code = ''
            """
        )
        op.alter_column("buildings", "code", nullable=False)
        op.create_index("ix_buildings_code", "buildings", ["code"], unique=True)
    if "manager_id" not in columns:
        op.create_index("ix_buildings_manager_id", "buildings", ["manager_id"])
        op.create_foreign_key(
            "fk_buildings_manager_id_users",
            "buildings",
            "users",
            ["manager_id"],
            ["id"],
        )
    if "house_type" not in columns:
        op.create_index("ix_buildings_house_type", "buildings", ["house_type"])
    if "status" not in columns:
        op.create_index("ix_buildings_status", "buildings", ["status"])


def create_floors_table() -> None:
    op.create_table(
        "floors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.Column("floor_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("expected_room_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("building_id", "floor_number", name="uq_floor_building_number"),
    )
    op.create_index("ix_floors_building_id", "floors", ["building_id"])


def create_building_amenities_table() -> None:
    op.create_table(
        "building_amenities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.Column("amenity_key", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("building_id", "amenity_key", name="uq_building_amenity"),
    )
    op.create_index("ix_building_amenities_building_id", "building_amenities", ["building_id"])
    op.create_index("ix_building_amenities_amenity_key", "building_amenities", ["amenity_key"])


def create_building_expense_templates_table() -> None:
    op.create_table(
        "building_expense_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("default_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_building_expense_templates_building_id",
        "building_expense_templates",
        ["building_id"],
    )
    op.create_index(
        "ix_building_expense_templates_category",
        "building_expense_templates",
        ["category"],
    )


def add_room_floor_id() -> None:
    if not has_column("rooms", "floor_id"):
        op.add_column("rooms", sa.Column("floor_id", sa.Integer(), nullable=True))
        op.create_index("ix_rooms_floor_id", "rooms", ["floor_id"])
        op.create_foreign_key("fk_rooms_floor_id_floors", "rooms", "floors", ["floor_id"], ["id"])


def backfill_floors_and_room_links() -> None:
    op.execute(
        """
        INSERT INTO floors (
            building_id,
            floor_number,
            name,
            expected_room_count,
            created_at,
            updated_at
        )
        SELECT
            building_id,
            COALESCE(floor, 1),
            'Floor ' || COALESCE(floor, 1)::text,
            COUNT(*),
            now(),
            now()
        FROM rooms
        GROUP BY building_id, COALESCE(floor, 1)
        ON CONFLICT (building_id, floor_number) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE rooms
        SET floor_id = floors.id
        FROM floors
        WHERE rooms.building_id = floors.building_id
          AND COALESCE(rooms.floor, 1) = floors.floor_number
          AND rooms.floor_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE buildings
        SET number_of_floors = floor_counts.floor_count
        FROM (
            SELECT building_id, COUNT(*) AS floor_count
            FROM floors
            GROUP BY building_id
        ) AS floor_counts
        WHERE buildings.id = floor_counts.building_id
        """
    )


def drop_building_columns() -> None:
    for index_name in [
        "ix_buildings_status",
        "ix_buildings_house_type",
        "ix_buildings_manager_id",
        "ix_buildings_code",
    ]:
        try:
            op.drop_index(index_name, table_name="buildings")
        except Exception:
            pass
    for column in [
        "emergency_contact_phone",
        "emergency_contact_name",
        "zalo",
        "email",
        "phone",
        "status",
        "manager_id",
        "owner_email",
        "owner_phone",
        "owner_name",
        "number_of_floors",
        "house_type",
        "code",
    ]:
        if has_column("buildings", column):
            op.drop_column("buildings", column)


def table_columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def has_column(table_name: str, column_name: str) -> bool:
    return column_name in table_columns(table_name)
