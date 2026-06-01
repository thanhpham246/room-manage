from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel

CONTRACT_SCOPES = {"room", "whole_building"}
CONTRACT_STATUSES = {"pending", "active", "ended", "terminated", "cancelled", "deleted"}


class ContractCreate(BaseModel):
    scope: str = "room"
    building_id: int | None = None
    room_id: int | None = None
    tenant_id: int
    start_date: date
    end_date: date | None = None
    monthly_rent: int = Field(ge=0)
    deposit_amount: int = Field(default=0, ge=0)
    note: str | None = None

    @model_validator(mode="after")
    def validate_contract_shape(self) -> "ContractCreate":
        validate_scope_and_dates(
            self.scope,
            self.building_id,
            self.room_id,
            self.start_date,
            self.end_date,
        )
        return self


class ContractUpdate(BaseModel):
    scope: str | None = None
    building_id: int | None = None
    room_id: int | None = None
    tenant_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    monthly_rent: int | None = Field(default=None, ge=0)
    deposit_amount: int | None = Field(default=None, ge=0)
    status: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def validate_status(self) -> "ContractUpdate":
        if self.scope is not None and self.scope not in CONTRACT_SCOPES:
            raise ValueError("Invalid contract scope")
        if self.status is not None and self.status not in CONTRACT_STATUSES:
            raise ValueError("Invalid contract status")
        return self


class ContractRead(ORMModel):
    id: int
    contract_code: str
    scope: str
    building_id: int
    building_name: str | None = None
    room_id: int | None = None
    room_code: str | None = None
    tenant_id: int
    tenant_name: str | None = None
    start_date: date
    end_date: date | None = None
    monthly_rent: int
    deposit_amount: int
    status: str
    note: str | None = None
    deleted_at: datetime | None = None
    invoice_count: int = 0
    total_invoiced: int = 0
    total_paid: int = 0
    outstanding_amount: int = 0


class ContractList(BaseModel):
    items: list[ContractRead]
    total: int


def validate_scope_and_dates(
    scope: str,
    building_id: int | None,
    room_id: int | None,
    start_date: date,
    end_date: date | None,
) -> None:
    if scope not in CONTRACT_SCOPES:
        raise ValueError("Invalid contract scope")
    if end_date is not None and end_date < start_date:
        raise ValueError("Contract end date must be after start date")
    if scope == "room" and room_id is None:
        raise ValueError("Room contract requires room_id")
    if scope == "whole_building" and building_id is None:
        raise ValueError("Whole-building contract requires building_id")
    if scope == "whole_building" and room_id is not None:
        raise ValueError("Whole-building contract cannot include room_id")
