from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.repositories.billing import BillingRepository
from app.repositories.contracts import ContractRepository
from app.schemas.billing import PaymentCreate, PaymentList, PaymentRead
from app.services.billing import BillingService
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


@router.post("", response_model=PaymentRead, status_code=201)
async def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)) -> PaymentRead:
    try:
        payment = BillingService(
            BillingRepository(db),
            ContractRepository(db),
        ).create_payment(payload)
    except DomainError as error:
        raise_http_error(error)
    return PaymentRead.model_validate(payment).model_copy(
        update={"invoice_status": payment.invoice.status}
    )


@router.get("", response_model=PaymentList)
async def list_payments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaymentList:
    payments, total = BillingService(BillingRepository(db), ContractRepository(db)).list_payments(
        skip=skip,
        limit=limit,
    )
    return PaymentList(
        items=[
            PaymentRead.model_validate(payment).model_copy(
                update={"invoice_status": payment.invoice.status}
            )
            for payment in payments
        ],
        total=total,
    )
