from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel

ROOM_TYPES = {"standard", "studio", "loft", "shared_room", "dorm_bed"}
ROOM_STATUSES = {"vacant", "occupied", "reserved", "maintenance", "unavailable"}


class RoomRead(ORMModel):
    id: int
    building_id: int
    floor_id: int | None = None
    code: str
    name: str
    room_type: str
    floor: int | None = None
    area_sqm: int | None = None
    max_occupants: int
    rent_price: int
    deposit_amount: int
    status: str
    note: str | None = None
    building_name: str | None = None
    floor_name: str | None = None
    current_tenant_name: str | None = None
    active_contract_id: int | None = None
    current_debt: int = 0


class RoomCreate(BaseModel):
    building_id: int
    floor_id: int | None = None
    name: str = Field(min_length=1, max_length=100)
    room_type: str = "standard"
    floor: int | None = None
    area_sqm: int | None = None
    max_occupants: int = Field(default=1, ge=1)
    rent_price: int = Field(ge=0)
    deposit_amount: int = Field(default=0, ge=0)
    status: str = "vacant"
    note: str | None = None

    @model_validator(mode="after")
    def validate_enums(self) -> "RoomCreate":
        if self.room_type not in ROOM_TYPES:
            raise ValueError("Invalid room type")
        if self.status not in ROOM_STATUSES:
            raise ValueError("Invalid room status")
        return self


class RoomUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    room_type: str | None = None
    area_sqm: int | None = Field(default=None, ge=0)
    max_occupants: int | None = Field(default=None, ge=1)
    rent_price: int | None = Field(default=None, ge=0)
    deposit_amount: int | None = Field(default=None, ge=0)
    status: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def validate_enums(self) -> "RoomUpdate":
        if self.room_type is not None and self.room_type not in ROOM_TYPES:
            raise ValueError("Invalid room type")
        if self.status is not None and self.status not in ROOM_STATUSES:
            raise ValueError("Invalid room status")
        return self


class RoomList(BaseModel):
    items: list[RoomRead]
    total: int


class RoomDashboard(BaseModel):
    room: RoomRead
    tenant_name: str | None = None
    active_contract_id: int | None = None
    contract_start_date: str | None = None
    contract_end_date: str | None = None
    current_debt: int = 0
    last_payment_amount: int | None = None
    last_payment_date: str | None = None
    latest_billing_month: str | None = None
    latest_electricity_current: int | None = None
    latest_water_current: int | None = None
