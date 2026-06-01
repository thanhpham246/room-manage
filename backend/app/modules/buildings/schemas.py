from pydantic import BaseModel, Field, model_validator

from app.modules.rooms.schemas import RoomRead
from app.schemas.common import ORMModel

HOUSE_TYPES = {"boarding_house", "mini_apartment", "dormitory", "whole_house"}
BUILDING_STATUSES = {"active", "temporarily_closed", "under_renovation"}
AMENITY_KEYS = {"wifi", "camera", "elevator", "shared_washing_machine", "parking", "security"}


class BuildingExpenseTemplateCreate(BaseModel):
    category: str = Field(default="common", min_length=1, max_length=100)
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
