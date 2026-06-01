from __future__ import annotations

from datetime import UTC, date, datetime

from app.models import Contract
from app.modules.contracts.repository import ContractRepository
from app.modules.contracts.schemas import (
    CONTRACT_STATUSES,
    ContractCreate,
    ContractRead,
    ContractUpdate,
    validate_scope_and_dates,
)
from app.modules.tenants.repository import TenantRepository
from app.services.errors import ConflictError, DomainError, NotFoundError


class ContractService:
    def __init__(self, contracts: ContractRepository, tenants: TenantRepository) -> None:
        self.contracts = contracts
        self.tenants = tenants

    def create(self, payload: ContractCreate) -> Contract:
        tenant = self.tenants.get(payload.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        building_id, room_id = self._resolve_asset(
            payload.scope,
            payload.building_id,
            payload.room_id,
        )
        if self.contracts.has_asset_overlap(
            scope=payload.scope,
            building_id=building_id,
            room_id=room_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
        ):
            raise ConflictError("Contract overlaps an existing asset contract")

        status = self._initial_status(payload.start_date, payload.end_date)
        contract = Contract(
            contract_code=self.contracts.next_code(),
            scope=payload.scope,
            building_id=building_id,
            room_id=room_id,
            tenant_id=payload.tenant_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            monthly_rent=payload.monthly_rent,
            deposit_amount=payload.deposit_amount,
            status=status,
            note=payload.note,
        )
        self._apply_asset_status(contract)
        return self.contracts.create(contract)

    def update(self, contract_id: int, payload: ContractUpdate) -> Contract:
        contract = self.get_or_raise(contract_id)
        data = payload.model_dump(exclude_unset=True)
        if not data:
            return contract
        old_scope = contract.scope
        old_building_id = contract.building_id
        old_room_id = contract.room_id
        invoice_count = self.contracts.invoice_count(contract.id)
        locked_fields = {
            "scope",
            "building_id",
            "room_id",
            "tenant_id",
            "start_date",
            "monthly_rent",
            "deposit_amount",
        }
        if invoice_count > 0 and any(field in data for field in locked_fields):
            raise ConflictError(
                "Contract financial and asset fields are locked after invoices exist"
            )

        next_scope = data.get("scope", contract.scope)
        next_building_id = data.get("building_id", contract.building_id)
        next_room_id = data.get("room_id", contract.room_id)
        next_start_date = data.get("start_date", contract.start_date)
        next_end_date = data.get("end_date", contract.end_date)
        validate_scope_and_dates(
            next_scope,
            next_building_id,
            next_room_id,
            next_start_date,
            next_end_date,
        )
        building_id, room_id = self._resolve_asset(next_scope, next_building_id, next_room_id)
        if self.contracts.has_asset_overlap(
            scope=next_scope,
            building_id=building_id,
            room_id=room_id,
            start_date=next_start_date,
            end_date=next_end_date,
            exclude_id=contract.id,
        ):
            raise ConflictError("Contract overlaps an existing asset contract")
        if "tenant_id" in data and self.tenants.get(data["tenant_id"]) is None:
            raise NotFoundError("Tenant not found")
        if "status" in data and data["status"] not in CONTRACT_STATUSES:
            raise DomainError("Invalid contract status")

        for key, value in data.items():
            setattr(contract, key, value)
        contract.scope = next_scope
        contract.building_id = building_id
        contract.room_id = room_id
        if "status" not in data:
            contract.status = self._initial_status(contract.start_date, contract.end_date)
        if (
            old_scope != contract.scope
            or old_building_id != contract.building_id
            or old_room_id != contract.room_id
            or contract.status not in {"active", "pending"}
        ):
            self._release_asset_status(old_scope, old_building_id, old_room_id, contract.id)
        self._apply_asset_status(contract)
        return self.contracts.save(contract)

    def soft_delete(self, contract_id: int) -> None:
        contract = self.contracts.get(contract_id, include_deleted=True)
        if contract is None:
            raise NotFoundError("Contract not found")
        if contract.deleted_at is None:
            old_scope = contract.scope
            old_building_id = contract.building_id
            old_room_id = contract.room_id
            contract.deleted_at = datetime.now(UTC)
            contract.status = "deleted"
            self._release_asset_status(old_scope, old_building_id, old_room_id, contract.id)
            self.contracts.save(contract)

    def get_or_raise(self, contract_id: int, *, include_deleted: bool = False) -> Contract:
        contract = self.contracts.get(contract_id, include_deleted=include_deleted)
        if contract is None:
            raise NotFoundError("Contract not found")
        return contract

    def list(
        self,
        status: str | None,
        search: str | None,
        include_deleted: bool,
        skip: int,
        limit: int,
    ) -> tuple[list[Contract], int]:
        if status is not None and status not in CONTRACT_STATUSES:
            raise DomainError("Invalid contract status")
        return self.contracts.list(
            status=status,
            search=search,
            include_deleted=include_deleted,
            skip=skip,
            limit=limit,
        )

    def to_read(self, contract: Contract) -> ContractRead:
        total_invoiced, total_paid, outstanding = self.contracts.totals(contract.id)
        return ContractRead(
            id=contract.id,
            contract_code=contract.contract_code,
            scope=contract.scope,
            building_id=contract.building_id,
            building_name=contract.building.name if contract.building else None,
            room_id=contract.room_id,
            room_code=contract.room.code if contract.room else None,
            tenant_id=contract.tenant_id,
            tenant_name=contract.tenant.full_name if contract.tenant else None,
            start_date=contract.start_date,
            end_date=contract.end_date,
            monthly_rent=contract.monthly_rent,
            deposit_amount=contract.deposit_amount,
            status="deleted" if contract.deleted_at else contract.status,
            note=contract.note,
            deleted_at=contract.deleted_at,
            invoice_count=self.contracts.invoice_count(contract.id),
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            outstanding_amount=outstanding,
        )

    def _resolve_asset(
        self,
        scope: str,
        building_id: int | None,
        room_id: int | None,
    ) -> tuple[int, int | None]:
        if scope == "room":
            if room_id is None:
                raise DomainError("Room contract requires room_id")
            room = self.contracts.get_room(room_id)
            if room is None:
                raise NotFoundError("Room not found")
            if building_id is not None and building_id != room.building_id:
                raise DomainError("Room does not belong to building")
            return room.building_id, room.id
        if scope == "whole_building":
            if building_id is None:
                raise DomainError("Whole-building contract requires building_id")
            if self.contracts.get_building(building_id) is None:
                raise NotFoundError("Building not found")
            return building_id, None
        raise DomainError("Invalid contract scope")

    @staticmethod
    def _initial_status(start_date: date, end_date: date | None) -> str:
        today = date.today()
        if end_date is not None and end_date < today:
            return "ended"
        if start_date > today:
            return "pending"
        return "active"

    def _apply_asset_status(self, contract: Contract) -> None:
        if contract.status not in {"active", "pending"}:
            return
        status = "occupied" if contract.status == "active" else "reserved"
        if contract.scope == "room" and contract.room_id is not None:
            room = self.contracts.get_room(contract.room_id)
            if room is not None and (contract.status == "active" or room.status == "vacant"):
                room.status = status
            return
        if contract.scope == "whole_building":
            self._apply_building_status(contract.building_id, status)

    def _apply_building_status(self, building_id: int, status: str) -> None:
        building = self.contracts.get_building(building_id)
        if building is None:
            return
        for room in building.rooms:
            if status == "occupied" or room.status == "vacant":
                room.status = status

    def _release_asset_status(
        self,
        scope: str,
        building_id: int,
        room_id: int | None,
        contract_id: int,
    ) -> None:
        has_other_contract = self.contracts.has_active_or_pending_asset_contract(
            scope=scope,
            building_id=building_id,
            room_id=room_id,
            exclude_id=contract_id,
        )
        if has_other_contract:
            return
        if scope == "room" and room_id is not None:
            room = self.contracts.get_room(room_id)
            if room is not None and room.status in {"occupied", "reserved"}:
                room.status = "vacant"
            return
        building = self.contracts.get_building(building_id)
        if building is None:
            return
        for room in building.rooms:
            if room.status in {"occupied", "reserved"}:
                room.status = "vacant"
