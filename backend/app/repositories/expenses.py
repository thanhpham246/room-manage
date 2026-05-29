from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Expense


class ExpenseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def list(
        self,
        building_id: int | None = None,
        spent_on: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Expense], int]:
        query = select(Expense)
        count_query = select(func.count()).select_from(Expense)
        if building_id is not None:
            query = query.where(Expense.building_id == building_id)
            count_query = count_query.where(Expense.building_id == building_id)
        if spent_on is not None:
            query = query.where(Expense.spent_on == spent_on)
            count_query = count_query.where(Expense.spent_on == spent_on)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Expense.id).offset(skip).limit(limit)))
        return items, total
