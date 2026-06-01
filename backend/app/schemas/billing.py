from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class InvoiceReadingInput(BaseModel):
    contract_id: int
    electricity_previous: int = Field(default=0, ge=0)
    electricity_current: int = Field(default=0, ge=0)
    water_previous: int = Field(default=0, ge=0)
    water_current: int = Field(default=0, ge=0)
    surcharge_amount: int = Field(default=0, ge=0)
    discount_amount: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_meter_ranges(self) -> "InvoiceReadingInput":
        if self.electricity_current < self.electricity_previous:
            raise ValueError("Electricity current reading must be greater than previous reading")
        if self.water_current < self.water_previous:
            raise ValueError("Water current reading must be greater than previous reading")
        return self


class InvoiceBatchCreate(BaseModel):
    billing_month: date
    electricity_unit_price: int = Field(default=0, ge=0)
    water_unit_price: int = Field(default=0, ge=0)
    fixed_service_amount: int = Field(default=0, ge=0)
    readings: list[InvoiceReadingInput] = Field(min_length=1)


class InvoiceRead(ORMModel):
    id: int
    contract_id: int
    building_id: int
    room_id: int | None = None
    tenant_id: int
    billing_month: date
    rent_amount: int
    electricity_amount: int
    water_amount: int
    service_amount: int
    surcharge_amount: int
    discount_amount: int
    total_amount: int
    paid_amount: int
    status: str
    issued_date: date


class InvoiceList(BaseModel):
    items: list[InvoiceRead]
    total: int


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: int = Field(gt=0)
    method: str = Field(default="cash", max_length=50)
    note: str | None = None


class PaymentRead(ORMModel):
    id: int
    invoice_id: int
    amount: int
    method: str
    paid_at: datetime
    note: str | None = None
    invoice_status: str = ""


class PaymentList(BaseModel):
    items: list[PaymentRead]
    total: int
