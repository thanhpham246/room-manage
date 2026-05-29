from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class TenantCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = None
    identity_number: str | None = None
    emergency_contact: str | None = None


class TenantRead(ORMModel):
    id: int
    full_name: str
    phone: str
    email: EmailStr | None = None
    identity_number: str | None = None
    emergency_contact: str | None = None


class TenantList(BaseModel):
    items: list[TenantRead]
    total: int
