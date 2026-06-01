from __future__ import annotations

from datetime import date, timedelta

from app.models import Building, BuildingAmenity, BuildingExpenseTemplate, Floor, Room
from app.modules.buildings.repository import BuildingRepository
from app.modules.buildings.schemas import (
    BuildingCreate,
    BuildingDashboard,
    BuildingExpenseTemplateRead,
    BuildingRead,
    BuildingTree,
    BuildingUpdate,
    FloorTreeRead,
)
from app.modules.rooms.schemas import RoomRead
from app.repositories.users import UserRepository
from app.services.errors import ConflictError, DomainError, NotFoundError


class BuildingService:
    def __init__(
        self,
        buildings: BuildingRepository,
        users: UserRepository | None = None,
    ) -> None:
        self.buildings = buildings
        self.users = users

    def create(self, payload: BuildingCreate) -> Building:
        self._validate_manager(payload.manager_id)
        amenities = self._normalize_amenities(payload.amenities)
        code = payload.code or self.buildings.next_code()
        if self.buildings.get_by_code(code) is not None:
            raise ConflictError("Building code already exists")

        building = Building(
            code=code,
            name=payload.name,
            address=payload.address,
            house_type=payload.house_type,
            number_of_floors=payload.number_of_floors or len(payload.floors),
            owner_name=payload.owner_name,
            owner_phone=payload.owner_phone,
            owner_email=payload.owner_email,
            manager_id=payload.manager_id,
            status=payload.status,
            phone=payload.phone,
            email=payload.email,
            zalo=payload.zalo,
            emergency_contact_name=payload.emergency_contact_name,
            emergency_contact_phone=payload.emergency_contact_phone,
            note=payload.note,
        )
        building.floors = []
        building.rooms = []
        for floor_payload in payload.floors:
            floor = Floor(
                floor_number=floor_payload.floor_number,
                name=floor_payload.name or f"Floor {floor_payload.floor_number}",
                expected_room_count=floor_payload.expected_room_count,
                note=floor_payload.note,
            )
            generated_rooms = self._build_generated_rooms(payload, code, floor_payload.floor_number)
            floor.rooms = generated_rooms
            building.rooms.extend(generated_rooms)
            building.floors.append(floor)
        building.amenities = [
            BuildingAmenity(amenity_key=amenity_key) for amenity_key in amenities
        ]
        building.expense_templates = [
            BuildingExpenseTemplate(**template.model_dump())
            for template in payload.expense_templates
        ]
        return self.buildings.create(building)

    def update(self, building_id: int, payload: BuildingUpdate) -> Building:
        building = self.get_or_raise(building_id)
        data = payload.model_dump(exclude_unset=True)
        amenities = data.pop("amenities", None)
        has_templates = "expense_templates" in data
        data.pop("expense_templates", None)
        if "manager_id" in data:
            self._validate_manager(data["manager_id"])
        if "code" in data and data["code"] != building.code:
            if self.buildings.has_rooms(building.id):
                raise ConflictError("Building code cannot be changed after rooms exist")
            existing = self.buildings.get_by_code(data["code"])
            if existing is not None and existing.id != building.id:
                raise ConflictError("Building code already exists")
        if "house_type" in data and data["house_type"] != building.house_type:
            if self.buildings.has_active_contracts(building.id):
                raise ConflictError("House type cannot be changed while active contracts exist")
        for key, value in data.items():
            setattr(building, key, value)
        if amenities is not None:
            amenities = self._normalize_amenities(amenities)
            self.buildings.replace_amenities(
                building,
                [BuildingAmenity(amenity_key=amenity_key) for amenity_key in amenities],
            )
        if has_templates:
            self.buildings.replace_expense_templates(
                building,
                [
                    BuildingExpenseTemplate(**template.model_dump())
                    for template in (payload.expense_templates or [])
                ],
            )
        return self.buildings.save(building)

    def get_or_raise(self, building_id: int) -> Building:
        building = self.buildings.get(building_id)
        if building is None:
            raise NotFoundError("Building not found")
        return building

    def list(
        self,
        search: str | None,
        house_type: str | None,
        status: str | None,
        manager_id: int | None,
        skip: int,
        limit: int,
    ) -> tuple[list[Building], int]:
        return self.buildings.list(
            search=search,
            house_type=house_type,
            status=status,
            manager_id=manager_id,
            skip=skip,
            limit=limit,
        )

    def to_read(self, building: Building) -> BuildingRead:
        total_rooms, occupied_rooms, _ = self.buildings.building_room_counts(building.id)
        expected_rooms = sum(floor.expected_room_count for floor in building.floors)
        return BuildingRead(
            id=building.id,
            code=building.code,
            name=building.name,
            address=building.address,
            house_type=building.house_type,
            number_of_floors=building.number_of_floors,
            owner_name=building.owner_name,
            owner_phone=building.owner_phone,
            owner_email=building.owner_email,
            manager_id=building.manager_id,
            manager_name=building.manager.full_name if building.manager else None,
            status=building.status,
            phone=building.phone,
            email=building.email,
            zalo=building.zalo,
            emergency_contact_name=building.emergency_contact_name,
            emergency_contact_phone=building.emergency_contact_phone,
            note=building.note,
            expected_rooms=expected_rooms,
            total_rooms=total_rooms,
            occupied_rooms=occupied_rooms,
            amenities=[amenity.amenity_key for amenity in building.amenities],
            expense_templates=[
                BuildingExpenseTemplateRead.model_validate(template)
                for template in building.expense_templates
            ],
        )

    def dashboard(self, building_id: int, month: date) -> BuildingDashboard:
        building = self.get_or_raise(building_id)
        total_rooms, occupied_rooms, vacant_rooms = self.buildings.building_room_counts(building_id)
        occupancy_rate = 0 if total_rooms == 0 else round((occupied_rooms / total_rooms) * 100)
        today = date.today()
        return BuildingDashboard(
            building_id=building.id,
            building_name=building.name,
            total_rooms=total_rooms,
            occupied_rooms=occupied_rooms,
            vacant_rooms=vacant_rooms,
            occupancy_rate=occupancy_rate,
            monthly_revenue=self.buildings.monthly_revenue(building_id, month),
            debt=self.buildings.debt(building_id),
            expiring_contracts=self.buildings.expiring_contracts(
                building_id,
                today,
                today + timedelta(days=30),
            ),
        )

    def tree(self, building_id: int) -> BuildingTree:
        building = self.get_or_raise(building_id)
        return BuildingTree(
            building_id=building.id,
            building_name=building.name,
            floors=[
                FloorTreeRead(
                    id=floor.id,
                    building_id=floor.building_id,
                    floor_number=floor.floor_number,
                    name=floor.name,
                    expected_room_count=floor.expected_room_count,
                    note=floor.note,
                    rooms=[RoomRead.model_validate(room) for room in floor.rooms],
                )
                for floor in building.floors
            ],
        )

    def _build_generated_rooms(
        self,
        payload: BuildingCreate,
        building_code: str,
        floor_number: int,
    ) -> list[Room]:
        rooms: list[Room] = []
        floor_payload = next(
            floor for floor in payload.floors if floor.floor_number == floor_number
        )
        for index in range(1, floor_payload.expected_room_count + 1):
            room_name = f"{floor_number}{index:02d}"
            rooms.append(
                Room(
                    code=self._build_room_code(building_code, room_name),
                    name=room_name,
                    room_type="standard",
                    floor=floor_number,
                    area_sqm=payload.default_room_area_sqm,
                    max_occupants=1,
                    rent_price=payload.default_room_rent_price or 0,
                    deposit_amount=payload.default_room_deposit_amount,
                    status="vacant",
                )
            )
        return rooms

    @staticmethod
    def _build_room_code(building_code: str, room_name: str) -> str:
        return f"{building_code}-{room_name.strip()}"

    def _validate_manager(self, manager_id: int | None) -> None:
        if manager_id is None:
            return
        if self.users is None:
            raise DomainError("User repository is required to validate manager")
        manager = self.users.get_by_id(manager_id)
        if manager is None or not manager.is_active or manager.role != "staff":
            raise DomainError("Responsible manager must be an active staff user")

    def _normalize_amenities(self, amenities: list[str]) -> list[str]:
        normalized = []
        seen = set()
        for amenity in amenities:
            name = amenity.strip()
            if not name:
                raise DomainError("Amenity name is required")
            key = name.casefold()
            if key in seen:
                raise DomainError("Amenities must be unique")
            seen.add(key)
            normalized.append(name)
        return normalized
