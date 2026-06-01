from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.search import build_search_text, normalized_contains
from app.models import Contract, Floor, Invoice, MeterReading, Payment, Room


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
            search_condition = normalized_contains(build_search_text(Room.code, Room.name), search)
            if search_condition is not None:
                conditions.append(search_condition)
        for condition in conditions:
            query = query.where(condition)
            count_query = count_query.where(condition)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Room.id).offset(skip).limit(limit)))
        return items, total

    def active_contract(self, room_id: int) -> Contract | None:
        room = self.db.get(Room, room_id)
        if room is None:
            return None
        return self.db.scalar(
            select(Contract)
            .where(
                Contract.status == "active",
                Contract.deleted_at.is_(None),
                or_(
                    Contract.room_id == room_id,
                    (Contract.scope == "whole_building")
                    & (Contract.building_id == room.building_id),
                ),
            )
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
