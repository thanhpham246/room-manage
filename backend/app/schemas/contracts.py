from datetime import date

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ContractCreate(BaseModel):
    room_id: int
    tenant_id: int
    start_date: date
    end_date: date | None = None
    monthly_rent: int = Field(ge=0)
    deposit_amount: int = Field(default=0, ge=0)
    note: str | None = None


class ContractRead(ORMModel):
    id: int
    room_id: int
    tenant_id: int
    start_date: date
    end_date: date | None = None
    monthly_rent: int
    deposit_amount: int
    status: str
    note: str | None = None


class ContractList(BaseModel):
    items: list[ContractRead]
    total: int
