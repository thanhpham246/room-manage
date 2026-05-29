from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    role: str = "staff"


class UserRead(ORMModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
