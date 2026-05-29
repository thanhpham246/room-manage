from datetime import date

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ExpenseCreate(BaseModel):
    building_id: int | None = None
    category: str = Field(min_length=1, max_length=100)
    amount: int = Field(gt=0)
    spent_on: date
    note: str | None = None


class ExpenseRead(ORMModel):
    id: int
    building_id: int | None = None
    category: str
    amount: int
    spent_on: date
    note: str | None = None


class ExpenseList(BaseModel):
    items: list[ExpenseRead]
    total: int
