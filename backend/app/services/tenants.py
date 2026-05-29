from app.models import Tenant
from app.repositories.tenants import TenantRepository
from app.schemas.tenants import TenantCreate


class TenantService:
    def __init__(self, tenants: TenantRepository) -> None:
        self.tenants = tenants

    def create(self, payload: TenantCreate) -> Tenant:
        return self.tenants.create(Tenant(**payload.model_dump()))

    def list(self, search: str | None, skip: int, limit: int) -> tuple[list[Tenant], int]:
        return self.tenants.list(search=search, skip=skip, limit=limit)
