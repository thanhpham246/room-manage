from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="staff", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    managed_buildings: Mapped[list["Building"]] = relationship(back_populates="manager")


class Building(Base, TimestampMixin):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    address: Mapped[str] = mapped_column(String(500))
    house_type: Mapped[str] = mapped_column(String(50), default="boarding_house", index=True)
    number_of_floors: Mapped[int] = mapped_column(Integer, default=0)
    owner_name: Mapped[str | None] = mapped_column(String(255))
    owner_phone: Mapped[str | None] = mapped_column(String(50))
    owner_email: Mapped[str | None] = mapped_column(String(255))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    zalo: Mapped[str | None] = mapped_column(String(100))
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text)

    manager: Mapped[User | None] = relationship(back_populates="managed_buildings")
    floors: Mapped[list["Floor"]] = relationship(
        back_populates="building",
        cascade="all, delete-orphan",
        order_by="Floor.floor_number",
    )
    rooms: Mapped[list["Room"]] = relationship(back_populates="building")
    amenities: Mapped[list["BuildingAmenity"]] = relationship(
        back_populates="building",
        cascade="all, delete-orphan",
        order_by="BuildingAmenity.amenity_key",
    )
    expense_templates: Mapped[list["BuildingExpenseTemplate"]] = relationship(
        back_populates="building",
        cascade="all, delete-orphan",
        order_by="BuildingExpenseTemplate.id",
    )
    expenses: Mapped[list["Expense"]] = relationship(back_populates="building")


class Floor(Base, TimestampMixin):
    __tablename__ = "floors"
    __table_args__ = (
        UniqueConstraint("building_id", "floor_number", name="uq_floor_building_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    floor_number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    expected_room_count: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(Text)

    building: Mapped[Building] = relationship(back_populates="floors")
    rooms: Mapped[list["Room"]] = relationship(
        back_populates="floor_ref",
        order_by="Room.name",
    )


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    floor_id: Mapped[int | None] = mapped_column(ForeignKey("floors.id"), index=True)
    code: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    room_type: Mapped[str] = mapped_column(String(50), default="standard", index=True)
    floor: Mapped[int | None] = mapped_column(Integer)
    area_sqm: Mapped[int | None] = mapped_column(Integer)
    max_occupants: Mapped[int] = mapped_column(Integer, default=1)
    rent_price: Mapped[int] = mapped_column(Integer)
    deposit_amount: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="vacant", index=True)
    note: Mapped[str | None] = mapped_column(Text)

    building: Mapped[Building] = relationship(back_populates="rooms")
    floor_ref: Mapped[Floor | None] = relationship(back_populates="rooms")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="room")
    meter_readings: Mapped[list["MeterReading"]] = relationship(back_populates="room")


class BuildingAmenity(Base, TimestampMixin):
    __tablename__ = "building_amenities"
    __table_args__ = (
        UniqueConstraint("building_id", "amenity_key", name="uq_building_amenity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    amenity_key: Mapped[str] = mapped_column(String(100), index=True)

    building: Mapped[Building] = relationship(back_populates="amenities")


class BuildingExpenseTemplate(Base, TimestampMixin):
    __tablename__ = "building_expense_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255))
    default_amount: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    building: Mapped[Building] = relationship(back_populates="expense_templates")


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    identity_number: Mapped[str | None] = mapped_column(String(100))
    emergency_contact: Mapped[str | None] = mapped_column(String(255))

    contracts: Mapped[list["Contract"]] = relationship(back_populates="tenant")


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    monthly_rent: Mapped[int] = mapped_column(Integer)
    deposit_amount: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    note: Mapped[str | None] = mapped_column(Text)

    room: Mapped[Room] = relationship(back_populates="contracts")
    tenant: Mapped[Tenant] = relationship(back_populates="contracts")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="contract")


class MeterReading(Base, TimestampMixin):
    __tablename__ = "meter_readings"
    __table_args__ = (UniqueConstraint("room_id", "billing_month", name="uq_reading_room_month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    billing_month: Mapped[date] = mapped_column(Date, index=True)
    electricity_previous: Mapped[int] = mapped_column(Integer, default=0)
    electricity_current: Mapped[int] = mapped_column(Integer, default=0)
    water_previous: Mapped[int] = mapped_column(Integer, default=0)
    water_current: Mapped[int] = mapped_column(Integer, default=0)

    room: Mapped[Room] = relationship(back_populates="meter_readings")


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("contract_id", "billing_month", name="uq_invoice_contract_month"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    billing_month: Mapped[date] = mapped_column(Date, index=True)
    rent_amount: Mapped[int] = mapped_column(Integer, default=0)
    electricity_amount: Mapped[int] = mapped_column(Integer, default=0)
    water_amount: Mapped[int] = mapped_column(Integer, default=0)
    service_amount: Mapped[int] = mapped_column(Integer, default=0)
    surcharge_amount: Mapped[int] = mapped_column(Integer, default=0)
    discount_amount: Mapped[int] = mapped_column(Integer, default=0)
    total_amount: Mapped[int] = mapped_column(Integer, default=0)
    paid_amount: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="unpaid", index=True)
    issued_date: Mapped[date] = mapped_column(Date, default=date.today)

    contract: Mapped[Contract] = relationship(back_populates="invoices")
    payments: Mapped[list["Payment"]] = relationship(back_populates="invoice")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    method: Mapped[str] = mapped_column(String(50), default="cash")
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    note: Mapped[str | None] = mapped_column(Text)

    invoice: Mapped[Invoice] = relationship(back_populates="payments")


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    spent_on: Mapped[date] = mapped_column(Date, default=date.today)
    note: Mapped[str | None] = mapped_column(Text)

    building: Mapped[Building | None] = relationship(back_populates="expenses")
