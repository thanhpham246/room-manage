from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel

HOUSE_TYPES = {"boarding_house", "mini_apartment", "dormitory", "whole_house"}
BUILDING_STATUSES = {"active", "temporarily_closed", "under_renovation"}
AMENITY_KEYS = {"wifi", "camera", "elevator", "shared_washing_machine", "parking", "security"}
ROOM_TYPES = {"standard", "studio", "loft", "shared_room", "dorm_bed"}
ROOM_STATUSES = {"vacant", "occupied", "reserved", "maintenance", "unavailable"}


class BuildingExpenseTemplateCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    default_amount: int = Field(ge=0)
    is_active: bool = True


class BuildingExpenseTemplateRead(ORMModel):
    id: int
    category: str
    name: str
    default_amount: int
    is_active: bool


class FloorSetup(BaseModel):
    floor_number: int = Field(ge=0)
    name: str | None = Field(default=None, max_length=100)
    expected_room_count: int = Field(ge=0)
    note: str | None = None


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


class FloorRead(ORMModel):
    id: int
    building_id: int
    floor_number: int
    name: str
    expected_room_count: int
    note: str | None = None


class FloorTreeRead(FloorRead):
    rooms: list[RoomRead]


class BuildingBase(BaseModel):
    code: str | None = Field(default=None, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    house_type: str = "boarding_house"
    number_of_floors: int | None = Field(default=None, ge=0)
    owner_name: str | None = Field(default=None, max_length=255)
    owner_phone: str | None = Field(default=None, max_length=50)
    owner_email: str | None = Field(default=None, max_length=255)
    manager_id: int | None = None
    status: str = "active"
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    zalo: str | None = Field(default=None, max_length=100)
    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_phone: str | None = Field(default=None, max_length=50)
    note: str | None = None

    @model_validator(mode="after")
    def validate_enums(self) -> "BuildingBase":
        if self.house_type not in HOUSE_TYPES:
            raise ValueError("Invalid house type")
        if self.status not in BUILDING_STATUSES:
            raise ValueError("Invalid building status")
        return self


class BuildingCreate(BuildingBase):
    default_room_rent_price: int | None = Field(default=None, ge=0)
    default_room_deposit_amount: int = Field(default=0, ge=0)
    default_room_area_sqm: int | None = Field(default=None, ge=0)
    floors: list[FloorSetup] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)
    expense_templates: list[BuildingExpenseTemplateCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_generated_room_defaults(self) -> "BuildingCreate":
        if self.floors and self.default_room_rent_price is None:
            raise ValueError("Default room rent price is required when floors are provided")
        floor_numbers = [floor.floor_number for floor in self.floors]
        if len(floor_numbers) != len(set(floor_numbers)):
            raise ValueError("Floor numbers must be unique")
        if len(self.amenities) != len(set(self.amenities)):
            raise ValueError("Amenities must be unique")
        return self


class BuildingUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=500)
    house_type: str | None = None
    owner_name: str | None = Field(default=None, max_length=255)
    owner_phone: str | None = Field(default=None, max_length=50)
    owner_email: str | None = Field(default=None, max_length=255)
    manager_id: int | None = None
    status: str | None = None
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    zalo: str | None = Field(default=None, max_length=100)
    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_phone: str | None = Field(default=None, max_length=50)
    note: str | None = None
    amenities: list[str] | None = None
    expense_templates: list[BuildingExpenseTemplateCreate] | None = None

    @model_validator(mode="after")
    def validate_enums(self) -> "BuildingUpdate":
        if self.house_type is not None and self.house_type not in HOUSE_TYPES:
            raise ValueError("Invalid house type")
        if self.status is not None and self.status not in BUILDING_STATUSES:
            raise ValueError("Invalid building status")
        return self


class BuildingRead(ORMModel):
    id: int
    code: str
    name: str
    address: str
    house_type: str
    number_of_floors: int
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_email: str | None = None
    manager_id: int | None = None
    manager_name: str | None = None
    status: str
    phone: str | None = None
    email: str | None = None
    zalo: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    note: str | None = None
    expected_rooms: int = 0
    total_rooms: int = 0
    occupied_rooms: int = 0
    amenities: list[str] = Field(default_factory=list)
    expense_templates: list[BuildingExpenseTemplateRead] = Field(default_factory=list)


class BuildingList(BaseModel):
    items: list[BuildingRead]
    total: int


class BuildingTree(BaseModel):
    building_id: int
    building_name: str
    floors: list[FloorTreeRead]


class BuildingDashboard(BaseModel):
    building_id: int
    building_name: str
    total_rooms: int
    occupied_rooms: int
    vacant_rooms: int
    occupancy_rate: int
    monthly_revenue: int
    debt: int
    expiring_contracts: int


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
