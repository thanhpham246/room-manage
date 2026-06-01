from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.search import build_search_text, normalized_contains
from app.models import Contract, Invoice, Payment, Room, Tenant


class TenantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, tenant_id: int, *, include_deleted: bool = False) -> Tenant | None:
        query = select(Tenant).where(Tenant.id == tenant_id)
        if not include_deleted:
            query = query.where(Tenant.deleted_at.is_(None))
        return self.db.scalar(query)

    def get_by_code(self, tenant_code: str) -> Tenant | None:
        return self.db.scalar(select(Tenant).where(Tenant.tenant_code == tenant_code))

    def get_by_identity(
        self,
        identity_number: str,
        *,
        exclude_id: int | None = None,
    ) -> Tenant | None:
        query = select(Tenant).where(
            Tenant.identity_number == identity_number,
            Tenant.deleted_at.is_(None),
        )
        if exclude_id is not None:
            query = query.where(Tenant.id != exclude_id)
        return self.db.scalar(query)

    def next_code(self) -> str:
        max_id = self.db.scalar(select(func.max(Tenant.id))) or 0
        return f"TENANT-{max_id + 1:03d}"

    def create(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def save(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def list(
        self,
        search: str | None = None,
        status: str | None = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Tenant], int]:
        query = select(Tenant)
        count_query = select(func.count()).select_from(Tenant)
        conditions = []

        if search:
            search_condition = normalized_contains(
                build_search_text(
                    Tenant.tenant_code,
                    Tenant.full_name,
                    Tenant.phone,
                    Tenant.email,
                    Tenant.identity_number,
                ),
                search,
            )
            if search_condition is not None:
                conditions.append(search_condition)

        status_condition = self._status_condition(status)
        if status_condition is not None:
            conditions.append(status_condition)
        elif not include_deleted:
            conditions.append(Tenant.deleted_at.is_(None))

        for condition in conditions:
            query = query.where(condition)
            count_query = count_query.where(condition)

        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Tenant.id).offset(skip).limit(limit)))
        return items, total

    def active_contract(self, tenant_id: int) -> Contract | None:
        return self.db.scalar(
            select(Contract)
            .where(Contract.tenant_id == tenant_id, Contract.status == "active")
            .options(
                selectinload(Contract.building),
                selectinload(Contract.room).selectinload(Room.building),
            )
            .order_by(Contract.id.desc())
        )

    def has_active_contract(self, tenant_id: int) -> bool:
        return bool(
            self.db.scalar(
                select(func.count()).select_from(Contract).where(
                    Contract.tenant_id == tenant_id,
                    Contract.status == "active",
                )
            )
        )

    def has_any_contract(self, tenant_id: int) -> bool:
        return bool(
            self.db.scalar(
                select(func.count()).select_from(Contract).where(Contract.tenant_id == tenant_id)
            )
        )

    def current_debt(self, tenant_id: int) -> int:
        return self.db.scalar(
            select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)).where(
                Invoice.tenant_id == tenant_id,
                Invoice.status != "paid",
            )
        ) or 0

    def unpaid_invoice_count(self, tenant_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Invoice).where(
                Invoice.tenant_id == tenant_id,
                Invoice.status != "paid",
            )
        ) or 0

    def total_paid(self, tenant_id: int) -> int:
        return self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(Invoice, Invoice.id == Payment.invoice_id)
            .where(Invoice.tenant_id == tenant_id)
        ) or 0

    def last_payment(self, tenant_id: int) -> Payment | None:
        return self.db.scalar(
            select(Payment)
            .join(Invoice, Invoice.id == Payment.invoice_id)
            .where(Invoice.tenant_id == tenant_id)
            .order_by(Payment.paid_at.desc(), Payment.id.desc())
        )

    def _status_condition(self, status: str | None):
        if status is None:
            return None
        active_contract = (
            select(Contract.id)
            .where(Contract.tenant_id == Tenant.id, Contract.status == "active")
            .exists()
        )
        any_contract = select(Contract.id).where(Contract.tenant_id == Tenant.id).exists()
        if status == "deleted":
            return Tenant.deleted_at.is_not(None)
        if status == "active":
            return Tenant.deleted_at.is_(None) & active_contract
        if status == "left":
            return Tenant.deleted_at.is_(None) & ~active_contract & any_contract
        if status == "not_renting":
            return Tenant.deleted_at.is_(None) & ~any_contract
        return Tenant.deleted_at.is_(None)
