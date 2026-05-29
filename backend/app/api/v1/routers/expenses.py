from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.repositories.expenses import ExpenseRepository
from app.schemas.expenses import ExpenseCreate, ExpenseList, ExpenseRead
from app.services.expenses import ExpenseService

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


@router.post("", response_model=ExpenseRead, status_code=201)
async def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    return ExpenseService(ExpenseRepository(db)).create(payload)


@router.get("", response_model=ExpenseList)
async def list_expenses(
    building_id: int | None = None,
    spent_on: date | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ExpenseList:
    items, total = ExpenseService(ExpenseRepository(db)).list(
        building_id,
        spent_on,
        skip,
        limit,
    )
    return ExpenseList(items=items, total=total)
