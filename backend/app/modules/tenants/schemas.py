from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel

TENANT_STATUSES = {"not_renting", "active", "left", "deleted"}


class TenantCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = None
    zalo: str | None = Field(default=None, max_length=100)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=32)
    identity_type: str | None = Field(default=None, max_length=32)
    identity_number: str | None = Field(default=None, max_length=100)
    identity_issued_date: date | None = None
    identity_issued_place: str | None = Field(default=None, max_length=255)
    permanent_address: str | None = Field(default=None, max_length=500)
    current_address: str | None = Field(default=None, max_length=500)
    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_phone: str | None = Field(default=None, max_length=50)
    emergency_contact_relationship: str | None = Field(default=None, max_length=100)
    note: str | None = None


class TenantUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    zalo: str | None = Field(default=None, max_length=100)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=32)
    identity_type: str | None = Field(default=None, max_length=32)
    identity_number: str | None = Field(default=None, max_length=100)
    identity_issued_date: date | None = None
    identity_issued_place: str | None = Field(default=None, max_length=255)
    permanent_address: str | None = Field(default=None, max_length=500)
    current_address: str | None = Field(default=None, max_length=500)
    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_phone: str | None = Field(default=None, max_length=50)
    emergency_contact_relationship: str | None = Field(default=None, max_length=100)
    note: str | None = None


class TenantRead(ORMModel):
    id: int
    tenant_code: str
    full_name: str
    phone: str
    email: EmailStr | None = None
    zalo: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    identity_type: str | None = None
    identity_number: str | None = None
    identity_issued_date: date | None = None
    identity_issued_place: str | None = None
    permanent_address: str | None = None
    current_address: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    emergency_contact_relationship: str | None = None
    note: str | None = None
    deleted_at: datetime | None = None
    status: str
    current_room_id: int | None = None
    current_room_code: str | None = None
    current_room_name: str | None = None
    current_building_id: int | None = None
    current_building_name: str | None = None
    active_contract_id: int | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    deposit_amount: int = 0
    current_debt: int = 0
    unpaid_invoices: int = 0
    total_paid: int = 0
    last_payment_date: datetime | None = None
    identity_edit_warning: bool = False


class TenantList(BaseModel):
    items: list[TenantRead]
    total: int
