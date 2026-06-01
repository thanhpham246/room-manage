from __future__ import annotations

from datetime import UTC, datetime

from app.models import Tenant
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.schemas import TENANT_STATUSES, TenantCreate, TenantRead, TenantUpdate
from app.services.errors import ConflictError, DomainError, NotFoundError


class TenantService:
    def __init__(self, tenants: TenantRepository) -> None:
        self.tenants = tenants

    def create(self, payload: TenantCreate) -> Tenant:
        data = self._clean_data(payload.model_dump())
        self._ensure_identity_available(data.get("identity_number"))
        tenant = Tenant(tenant_code=self.tenants.next_code(), **data)
        return self.tenants.create(tenant)

    def update(self, tenant_id: int, payload: TenantUpdate) -> Tenant:
        tenant = self.get_or_raise(tenant_id)
        data = self._clean_data(payload.model_dump(exclude_unset=True))
        if "identity_number" in data:
            self._ensure_identity_available(data["identity_number"], exclude_id=tenant.id)
        for key, value in data.items():
            setattr(tenant, key, value)
        return self.tenants.save(tenant)

    def soft_delete(self, tenant_id: int) -> None:
        tenant = self.tenants.get(tenant_id, include_deleted=True)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        if tenant.deleted_at is None:
            tenant.deleted_at = datetime.now(UTC)
            self.tenants.save(tenant)

    def get_or_raise(self, tenant_id: int, *, include_deleted: bool = False) -> Tenant:
        tenant = self.tenants.get(tenant_id, include_deleted=include_deleted)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        return tenant

    def list(
        self,
        search: str | None,
        status: str | None,
        include_deleted: bool,
        skip: int,
        limit: int,
    ) -> tuple[list[Tenant], int]:
        if status is not None and status not in TENANT_STATUSES:
            raise DomainError("Invalid tenant status")
        return self.tenants.list(
            search=search,
            status=status,
            include_deleted=include_deleted,
            skip=skip,
            limit=limit,
        )

    def to_read(self, tenant: Tenant) -> TenantRead:
        active_contract = self.tenants.active_contract(tenant.id)
        has_any_contract = self.tenants.has_any_contract(tenant.id)
        last_payment = self.tenants.last_payment(tenant.id)
        room = active_contract.room if active_contract else None
        building = active_contract.building if active_contract else None
        if building is None and room is not None:
            building = room.building
        status = self._status(tenant, active_contract is not None, has_any_contract)

        return TenantRead(
            id=tenant.id,
            tenant_code=tenant.tenant_code,
            full_name=tenant.full_name,
            phone=tenant.phone,
            email=tenant.email,
            zalo=tenant.zalo,
            date_of_birth=tenant.date_of_birth,
            gender=tenant.gender,
            identity_type=tenant.identity_type,
            identity_number=tenant.identity_number,
            identity_issued_date=tenant.identity_issued_date,
            identity_issued_place=tenant.identity_issued_place,
            permanent_address=tenant.permanent_address,
            current_address=tenant.current_address,
            emergency_contact_name=tenant.emergency_contact_name,
            emergency_contact_phone=tenant.emergency_contact_phone,
            emergency_contact_relationship=tenant.emergency_contact_relationship,
            note=tenant.note,
            deleted_at=tenant.deleted_at,
            status=status,
            current_room_id=room.id if room else None,
            current_room_code=room.code if room else None,
            current_room_name=room.name if room else None,
            current_building_id=building.id if building else None,
            current_building_name=building.name if building else None,
            active_contract_id=active_contract.id if active_contract else None,
            contract_start_date=active_contract.start_date if active_contract else None,
            contract_end_date=active_contract.end_date if active_contract else None,
            deposit_amount=active_contract.deposit_amount if active_contract else 0,
            current_debt=self.tenants.current_debt(tenant.id),
            unpaid_invoices=self.tenants.unpaid_invoice_count(tenant.id),
            total_paid=self.tenants.total_paid(tenant.id),
            last_payment_date=last_payment.paid_at if last_payment else None,
            identity_edit_warning=active_contract is not None,
        )

    def _ensure_identity_available(
        self,
        identity_number: str | None,
        *,
        exclude_id: int | None = None,
    ) -> None:
        if identity_number is None:
            return
        existing = self.tenants.get_by_identity(identity_number, exclude_id=exclude_id)
        if existing is not None:
            raise ConflictError("Tenant identity number already exists")

    def _clean_data(self, data: dict) -> dict:
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                value = value.strip()
                cleaned[key] = value or None
            else:
                cleaned[key] = value
        return cleaned

    @staticmethod
    def _status(tenant: Tenant, has_active_contract: bool, has_any_contract: bool) -> str:
        if tenant.deleted_at is not None:
            return "deleted"
        if has_active_contract:
            return "active"
        if has_any_contract:
            return "left"
        return "not_renting"
