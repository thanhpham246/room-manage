from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.modules.contracts.repository import ContractRepository
from app.modules.contracts.schemas import ContractCreate, ContractList, ContractRead, ContractUpdate
from app.modules.contracts.service import ContractService
from app.modules.tenants.repository import TenantRepository
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


def get_contract_service(db: Session) -> ContractService:
    return ContractService(ContractRepository(db), TenantRepository(db))


@router.post("", response_model=ContractRead, status_code=201)
async def create_contract(payload: ContractCreate, db: Session = Depends(get_db)) -> ContractRead:
    service = get_contract_service(db)
    try:
        contract = service.create(payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(contract)


@router.get("", response_model=ContractList)
async def list_contracts(
    status: str | None = None,
    search: str | None = None,
    include_deleted: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ContractList:
    service = get_contract_service(db)
    try:
        items, total = service.list(status, search, include_deleted, skip, limit)
    except DomainError as error:
        raise_http_error(error)
    return ContractList(items=[service.to_read(item) for item in items], total=total)


@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract(contract_id: int, db: Session = Depends(get_db)) -> ContractRead:
    service = get_contract_service(db)
    try:
        contract = service.get_or_raise(contract_id, include_deleted=True)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(contract)


@router.patch("/{contract_id}", response_model=ContractRead)
async def update_contract(
    contract_id: int,
    payload: ContractUpdate,
    db: Session = Depends(get_db),
) -> ContractRead:
    service = get_contract_service(db)
    try:
        contract = service.update(contract_id, payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(contract)


@router.delete("/{contract_id}", status_code=204)
async def delete_contract(contract_id: int, db: Session = Depends(get_db)) -> Response:
    service = get_contract_service(db)
    try:
        service.soft_delete(contract_id)
    except DomainError as error:
        raise_http_error(error)
    return Response(status_code=204)
