from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.repositories.contracts import ContractRepository
from app.repositories.properties import RoomRepository
from app.repositories.tenants import TenantRepository
from app.schemas.contracts import ContractCreate, ContractList, ContractRead
from app.services.contracts import ContractService
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


@router.post("", response_model=ContractRead, status_code=201)
async def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    service = ContractService(
        db,
        ContractRepository(db),
        RoomRepository(db),
        TenantRepository(db),
    )
    try:
        return service.create(payload)
    except DomainError as error:
        raise_http_error(error)


@router.get("", response_model=ContractList)
async def list_contracts(
    status: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ContractList:
    items, total = ContractService(
        db,
        ContractRepository(db),
        RoomRepository(db),
        TenantRepository(db),
    ).list(status, skip, limit)
    return ContractList(items=items, total=total)
