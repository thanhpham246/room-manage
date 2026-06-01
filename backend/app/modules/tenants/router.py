from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.schemas import TenantCreate, TenantList, TenantRead, TenantUpdate
from app.modules.tenants.service import TenantService
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


def get_tenant_service(db: Session) -> TenantService:
    return TenantService(TenantRepository(db))


@router.post("", response_model=TenantRead, status_code=201)
async def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)) -> TenantRead:
    service = get_tenant_service(db)
    try:
        tenant = service.create(payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(tenant)


@router.get("", response_model=TenantList)
async def list_tenants(
    search: str | None = None,
    status: str | None = None,
    include_deleted: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TenantList:
    service = get_tenant_service(db)
    try:
        items, total = service.list(search, status, include_deleted, skip, limit)
    except DomainError as error:
        raise_http_error(error)
    return TenantList(items=[service.to_read(item) for item in items], total=total)


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant(tenant_id: int, db: Session = Depends(get_db)) -> TenantRead:
    service = get_tenant_service(db)
    try:
        tenant = service.get_or_raise(tenant_id, include_deleted=True)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(tenant)


@router.patch("/{tenant_id}", response_model=TenantRead)
async def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
) -> TenantRead:
    service = get_tenant_service(db)
    try:
        tenant = service.update(tenant_id, payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(tenant)


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(tenant_id: int, db: Session = Depends(get_db)) -> Response:
    service = get_tenant_service(db)
    try:
        service.soft_delete(tenant_id)
    except DomainError as error:
        raise_http_error(error)
    return Response(status_code=204)
