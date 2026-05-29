from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Tenant


class TenantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, tenant_id: int) -> Tenant | None:
        return self.db.get(Tenant, tenant_id)

    def create(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def list(
        self,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Tenant], int]:
        query = select(Tenant)
        count_query = select(func.count()).select_from(Tenant)
        if search:
            condition = or_(
                Tenant.full_name.ilike(f"%{search}%"),
                Tenant.phone.ilike(f"%{search}%"),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Tenant.id).offset(skip).limit(limit)))
        return items, total
