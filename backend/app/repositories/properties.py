from __future__ import annotations

from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Building,
    BuildingAmenity,
    BuildingExpenseTemplate,
    Contract,
    Floor,
    Invoice,
    MeterReading,
    Payment,
    Room,
)


class BuildingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, building_id: int) -> Building | None:
        return self.db.scalar(
            select(Building)
            .where(Building.id == building_id)
            .options(
                selectinload(Building.manager),
                selectinload(Building.floors).selectinload(Floor.rooms),
                selectinload(Building.amenities),
                selectinload(Building.expense_templates),
                selectinload(Building.rooms),
            )
        )

    def get_by_code(self, code: str) -> Building | None:
        return self.db.scalar(select(Building).where(Building.code == code))

    def next_code(self) -> str:
        max_id = self.db.scalar(select(func.max(Building.id))) or 0
        return f"HOUSE-{max_id + 1:03d}"

    def create(self, building: Building) -> Building:
        self.db.add(building)
        self.db.commit()
        self.db.refresh(building)
        return self.get(building.id) or building

    def save(self, building: Building) -> Building:
        self.db.add(building)
        self.db.commit()
        return self.get(building.id) or building

    def list(
        self,
        search: str | None = None,
        house_type: str | None = None,
        status: str | None = None,
        manager_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Building], int]:
        query = select(Building).options(
            selectinload(Building.manager),
            selectinload(Building.floors),
            selectinload(Building.amenities),
            selectinload(Building.expense_templates),
            selectinload(Building.rooms),
        )
        count_query = select(func.count()).select_from(Building)
        conditions = []
        if search:
            pattern = f"%{search}%"
            conditions.append(
                Building.name.ilike(pattern)
                | Building.code.ilike(pattern)
                | Building.address.ilike(pattern)
            )
        if house_type:
            conditions.append(Building.house_type == house_type)
        if status:
            conditions.append(Building.status == status)
        if manager_id is not None:
            conditions.append(Building.manager_id == manager_id)
        for condition in conditions:
            query = query.where(condition)
            count_query = count_query.where(condition)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Building.id).offset(skip).limit(limit)))
        return items, total

    def replace_amenities(self, building: Building, amenities: list[BuildingAmenity]) -> None:
        for amenity in list(building.amenities):
            self.db.delete(amenity)
        building.amenities.clear()
        self.db.flush()
        building.amenities.extend(amenities)

    def replace_expense_templates(
        self,
        building: Building,
        templates: list[BuildingExpenseTemplate],
    ) -> None:
        for template in list(building.expense_templates):
            self.db.delete(template)
        building.expense_templates.clear()
        self.db.flush()
        building.expense_templates.extend(templates)

    def building_room_counts(self, building_id: int) -> tuple[int, int, int]:
        total_rooms = self.db.scalar(
            select(func.count()).select_from(Room).where(Room.building_id == building_id)
        ) or 0
        occupied_rooms = self.db.scalar(
            select(func.count())
            .select_from(Room)
            .where(Room.building_id == building_id, Room.status == "occupied")
        ) or 0
        vacant_rooms = self.db.scalar(
            select(func.count())
            .select_from(Room)
            .where(Room.building_id == building_id, Room.status == "vacant")
        ) or 0
        return total_rooms, occupied_rooms, vacant_rooms

    def monthly_revenue(self, building_id: int, month: date) -> int:
        return self.db.scalar(
            select(func.coalesce(func.sum(Invoice.paid_amount), 0))
            .join(Room, Room.id == Invoice.room_id)
            .where(Room.building_id == building_id, Invoice.billing_month == month)
        ) or 0

    def debt(self, building_id: int) -> int:
        return self.db.scalar(
            select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0))
            .join(Room, Room.id == Invoice.room_id)
            .where(Room.building_id == building_id, Invoice.status != "paid")
        ) or 0

    def expiring_contracts(self, building_id: int, start: date, end: date) -> int:
        return self.db.scalar(
            select(func.count())
            .select_from(Contract)
            .join(Room, Room.id == Contract.room_id)
            .where(
                Room.building_id == building_id,
                Contract.status == "active",
                and_(Contract.end_date.is_not(None), Contract.end_date >= start),
                Contract.end_date <= end,
            )
        ) or 0


class RoomRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, room_id: int) -> Room | None:
        return self.db.scalar(
            select(Room)
            .where(Room.id == room_id)
            .options(
                selectinload(Room.building),
                selectinload(Room.floor_ref),
                selectinload(Room.contracts).selectinload(Contract.tenant),
            )
        )

    def get_floor(self, floor_id: int) -> Floor | None:
        return self.db.get(Floor, floor_id)

    def get_by_code(self, code: str) -> Room | None:
        return self.db.scalar(select(Room).where(Room.code == code))

    def floor_belongs_to_building(self, floor_id: int, building_id: int) -> bool:
        floor = self.db.scalar(
            select(Floor.id).where(Floor.id == floor_id, Floor.building_id == building_id)
        )
        return floor is not None

    def create(self, room: Room) -> Room:
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return self.get(room.id) or room

    def save(self, room: Room) -> Room:
        self.db.add(room)
        self.db.commit()
        return self.get(room.id) or room

    def list(
        self,
        building_id: int | None = None,
        floor_id: int | None = None,
        status: str | None = None,
        room_type: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Room], int]:
        query = select(Room).options(selectinload(Room.building), selectinload(Room.floor_ref))
        count_query = select(func.count()).select_from(Room)
        conditions = []
        if building_id is not None:
            conditions.append(Room.building_id == building_id)
        if floor_id is not None:
            conditions.append(Room.floor_id == floor_id)
        if status:
            conditions.append(Room.status == status)
        if room_type:
            conditions.append(Room.room_type == room_type)
        if search:
            pattern = f"%{search}%"
            conditions.append(Room.name.ilike(pattern) | Room.code.ilike(pattern))
        for condition in conditions:
            query = query.where(condition)
            count_query = count_query.where(condition)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Room.id).offset(skip).limit(limit)))
        return items, total

    def active_contract(self, room_id: int) -> Contract | None:
        return self.db.scalar(
            select(Contract)
            .where(Contract.room_id == room_id, Contract.status == "active")
            .options(selectinload(Contract.tenant))
            .order_by(Contract.id.desc())
        )

    def current_debt(self, room_id: int) -> int:
        return self.db.scalar(
            select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)).where(
                Invoice.room_id == room_id,
                Invoice.status != "paid",
            )
        ) or 0

    def last_payment(self, room_id: int) -> Payment | None:
        return self.db.scalar(
            select(Payment)
            .join(Invoice, Invoice.id == Payment.invoice_id)
            .where(Invoice.room_id == room_id)
            .order_by(Payment.paid_at.desc(), Payment.id.desc())
        )

    def latest_meter_reading(self, room_id: int) -> MeterReading | None:
        return self.db.scalar(
            select(MeterReading)
            .where(MeterReading.room_id == room_id)
            .order_by(MeterReading.billing_month.desc(), MeterReading.id.desc())
        )
