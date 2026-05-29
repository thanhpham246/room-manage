from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.repositories.tenants import TenantRepository
from app.schemas.tenants import TenantCreate, TenantList, TenantRead
from app.services.tenants import TenantService

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


@router.post("", response_model=TenantRead, status_code=201)
async def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    return TenantService(TenantRepository(db)).create(payload)


@router.get("", response_model=TenantList)
async def list_tenants(
    search: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TenantList:
    items, total = TenantService(TenantRepository(db)).list(search, skip, limit)
    return TenantList(items=items, total=total)
