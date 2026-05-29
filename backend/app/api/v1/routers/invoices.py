from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.repositories.billing import BillingRepository
from app.repositories.contracts import ContractRepository
from app.schemas.billing import InvoiceBatchCreate, InvoiceList
from app.services.billing import BillingService
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


@router.post("/generate", response_model=InvoiceList, status_code=201)
async def generate_invoices(
    payload: InvoiceBatchCreate,
    db: Session = Depends(get_db),
) -> InvoiceList:
    try:
        invoices = BillingService(BillingRepository(db), ContractRepository(db)).generate_invoices(
            payload
        )
    except DomainError as error:
        raise_http_error(error)
    return InvoiceList(items=invoices, total=len(invoices))


@router.get("", response_model=InvoiceList)
async def list_invoices(
    billing_month: date | None = None,
    status: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> InvoiceList:
    items, total = BillingService(BillingRepository(db), ContractRepository(db)).list_invoices(
        billing_month=billing_month,
        status=status,
        skip=skip,
        limit=limit,
    )
    return InvoiceList(items=items, total=total)
