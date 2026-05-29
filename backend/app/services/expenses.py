from app.models import Expense
from app.repositories.expenses import ExpenseRepository
from app.schemas.expenses import ExpenseCreate


class ExpenseService:
    def __init__(self, expenses: ExpenseRepository) -> None:
        self.expenses = expenses

    def create(self, payload: ExpenseCreate) -> Expense:
        return self.expenses.create(Expense(**payload.model_dump()))

    def list(self, building_id, spent_on, skip: int, limit: int) -> tuple[list[Expense], int]:
        return self.expenses.list(
            building_id=building_id,
            spent_on=spent_on,
            skip=skip,
            limit=limit,
        )
