from __future__ import annotations

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.search import build_search_text, normalized_contains
from app.models import Building, Contract, Invoice, Room


class ContractRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, contract_id: int, *, include_deleted: bool = False) -> Contract | None:
        query = (
            select(Contract)
            .where(Contract.id == contract_id)
            .options(
                selectinload(Contract.building),
                selectinload(Contract.room),
                selectinload(Contract.tenant),
            )
        )
        if not include_deleted:
            query = query.where(Contract.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_code(self, contract_code: str) -> Contract | None:
        return self.db.scalar(select(Contract).where(Contract.contract_code == contract_code))

    def next_code(self) -> str:
        max_id = self.db.scalar(select(func.max(Contract.id))) or 0
        return f"CONTRACT-{max_id + 1:03d}"

    def get_building(self, building_id: int) -> Building | None:
        return self.db.get(Building, building_id)

    def get_room(self, room_id: int) -> Room | None:
        return self.db.scalar(
            select(Room).where(Room.id == room_id).options(selectinload(Room.building))
        )

    def create(self, contract: Contract) -> Contract:
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return self.get(contract.id) or contract

    def save(self, contract: Contract) -> Contract:
        self.db.add(contract)
        self.db.commit()
        return self.get(contract.id, include_deleted=True) or contract

    def list(
        self,
        status: str | None = None,
        search: str | None = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Contract], int]:
        query = select(Contract).options(
            selectinload(Contract.building),
            selectinload(Contract.room),
            selectinload(Contract.tenant),
        )
        count_query = select(func.count()).select_from(Contract)
        conditions = []
        if status:
            if status == "deleted":
                conditions.append(Contract.deleted_at.is_not(None))
            else:
                conditions.append(Contract.status == status)
                conditions.append(Contract.deleted_at.is_(None))
        elif not include_deleted:
            conditions.append(Contract.deleted_at.is_(None))
        if search:
            search_condition = normalized_contains(
                build_search_text(Contract.contract_code),
                search,
            )
            if search_condition is not None:
                conditions.append(search_condition)
        for condition in conditions:
            query = query.where(condition)
            count_query = count_query.where(condition)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Contract.id).offset(skip).limit(limit)))
        return items, total

    def has_asset_overlap(
        self,
        *,
        scope: str,
        building_id: int,
        room_id: int | None,
        start_date: date,
        end_date: date | None,
        exclude_id: int | None = None,
    ) -> bool:
        query = select(func.count()).select_from(Contract).where(
            Contract.deleted_at.is_(None),
            Contract.status.notin_(("cancelled", "deleted")),
            Contract.start_date <= (end_date or date.max),
            or_(Contract.end_date.is_(None), Contract.end_date >= start_date),
        )
        if exclude_id is not None:
            query = query.where(Contract.id != exclude_id)
        if scope == "whole_building":
            query = query.where(Contract.building_id == building_id)
        else:
            query = query.where(
                or_(
                    Contract.room_id == room_id,
                    (Contract.scope == "whole_building") & (Contract.building_id == building_id),
                )
            )
        return bool(self.db.scalar(query))

    def invoice_count(self, contract_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Invoice).where(Invoice.contract_id == contract_id)
        ) or 0

    def totals(self, contract_id: int) -> tuple[int, int, int]:
        row = self.db.execute(
            select(
                func.coalesce(func.sum(Invoice.total_amount), 0),
                func.coalesce(func.sum(Invoice.paid_amount), 0),
                func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0),
            ).where(Invoice.contract_id == contract_id)
        ).one()
        return int(row[0] or 0), int(row[1] or 0), int(row[2] or 0)

    def active_or_pending_room_contract(self, room_id: int) -> Contract | None:
        return self.db.scalar(
            select(Contract)
            .where(
                Contract.room_id == room_id,
                Contract.deleted_at.is_(None),
                Contract.status.in_(("active", "pending")),
            )
            .order_by(Contract.status.asc(), Contract.start_date.asc())
        )

    def has_active_or_pending_asset_contract(
        self,
        *,
        scope: str,
        building_id: int,
        room_id: int | None,
        exclude_id: int | None = None,
    ) -> bool:
        query = select(func.count()).select_from(Contract).where(
            Contract.deleted_at.is_(None),
            Contract.status.in_(("active", "pending")),
        )
        if exclude_id is not None:
            query = query.where(Contract.id != exclude_id)
        if scope == "whole_building":
            query = query.where(Contract.building_id == building_id)
        else:
            query = query.where(
                or_(
                    Contract.room_id == room_id,
                    (Contract.scope == "whole_building") & (Contract.building_id == building_id),
                )
            )
        return bool(self.db.scalar(query))

    def update_building_rooms_status(self, building_id: int, status: str) -> None:
        rooms = list(self.db.scalars(select(Room).where(Room.building_id == building_id)))
        for room in rooms:
            room.status = status
