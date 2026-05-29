from __future__ import annotations

from datetime import date, timedelta

from app.models import Building, BuildingAmenity, BuildingExpenseTemplate, Floor, Room
from app.repositories.properties import BuildingRepository, RoomRepository
from app.repositories.users import UserRepository
from app.schemas.properties import (
    AMENITY_KEYS,
    BuildingCreate,
    BuildingDashboard,
    BuildingExpenseTemplateRead,
    BuildingRead,
    BuildingTree,
    BuildingUpdate,
    FloorTreeRead,
    RoomCreate,
    RoomDashboard,
    RoomRead,
    RoomUpdate,
)
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
        self._validate_amenities(payload.amenities)
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
            BuildingAmenity(amenity_key=amenity_key) for amenity_key in payload.amenities
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
        templates = data.pop("expense_templates", None)
        if "manager_id" in data:
            self._validate_manager(data["manager_id"])
        if "code" in data and data["code"] != building.code:
            existing = self.buildings.get_by_code(data["code"])
            if existing is not None and existing.id != building.id:
                raise ConflictError("Building code already exists")
        for key, value in data.items():
            setattr(building, key, value)
        if amenities is not None:
            self._validate_amenities(amenities)
            self.buildings.replace_amenities(
                building,
                [BuildingAmenity(amenity_key=amenity_key) for amenity_key in amenities],
            )
        if templates is not None:
            self.buildings.replace_expense_templates(
                building,
                [BuildingExpenseTemplate(**template) for template in templates],
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

    def _validate_amenities(self, amenities: list[str]) -> None:
        invalid = sorted(set(amenities) - AMENITY_KEYS)
        if invalid:
            raise DomainError(f"Invalid amenities: {', '.join(invalid)}")


class RoomService:
    def __init__(self, rooms: RoomRepository, buildings: BuildingRepository) -> None:
        self.rooms = rooms
        self.buildings = buildings

    def create(self, payload: RoomCreate) -> Room:
        building = self.buildings.get(payload.building_id)
        if building is None:
            raise NotFoundError("Building not found")
        if payload.floor_id is None:
            raise DomainError("Floor is required")
        floor = self.rooms.get_floor(payload.floor_id)
        if floor is None or floor.building_id != payload.building_id:
            raise NotFoundError("Floor not found")
        code = self._build_room_code(building.code, payload.name)
        if self.rooms.get_by_code(code) is not None:
            raise ConflictError("Room code already exists")
        return self.rooms.create(
            Room(
                **payload.model_dump(exclude={"floor"}),
                code=code,
                floor=floor.floor_number,
            )
        )

    def update(self, room_id: int, payload: RoomUpdate) -> Room:
        room = self.get_or_raise(room_id)
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != room.name:
            next_code = self._build_room_code(room.building.code, data["name"])
            existing = self.rooms.get_by_code(next_code)
            if existing is not None and existing.id != room.id:
                raise ConflictError("Room code already exists")
            room.code = next_code
        for key, value in data.items():
            setattr(room, key, value)
        return self.rooms.save(room)

    def get_or_raise(self, room_id: int) -> Room:
        room = self.rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        return room

    def list(
        self,
        building_id: int | None,
        floor_id: int | None,
        status: str | None,
        room_type: str | None,
        search: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[Room], int]:
        return self.rooms.list(
            building_id=building_id,
            floor_id=floor_id,
            status=status,
            room_type=room_type,
            search=search,
            skip=skip,
            limit=limit,
        )

    def to_read(self, room: Room) -> RoomRead:
        active_contract = self.rooms.active_contract(room.id)
        return RoomRead(
            id=room.id,
            building_id=room.building_id,
            floor_id=room.floor_id,
            code=room.code,
            name=room.name,
            room_type=room.room_type,
            floor=room.floor,
            area_sqm=room.area_sqm,
            max_occupants=room.max_occupants,
            rent_price=room.rent_price,
            deposit_amount=room.deposit_amount,
            status=room.status,
            note=room.note,
            building_name=room.building.name if room.building else None,
            floor_name=room.floor_ref.name if room.floor_ref else None,
            current_tenant_name=active_contract.tenant.full_name if active_contract else None,
            active_contract_id=active_contract.id if active_contract else None,
            current_debt=self.rooms.current_debt(room.id),
        )

    def dashboard(self, room_id: int) -> RoomDashboard:
        room = self.get_or_raise(room_id)
        room_read = self.to_read(room)
        active_contract = self.rooms.active_contract(room.id)
        last_payment = self.rooms.last_payment(room.id)
        latest_reading = self.rooms.latest_meter_reading(room.id)
        return RoomDashboard(
            room=room_read,
            tenant_name=active_contract.tenant.full_name if active_contract else None,
            active_contract_id=active_contract.id if active_contract else None,
            contract_start_date=active_contract.start_date.isoformat() if active_contract else None,
            contract_end_date=(
                active_contract.end_date.isoformat()
                if active_contract and active_contract.end_date
                else None
            ),
            current_debt=room_read.current_debt,
            last_payment_amount=last_payment.amount if last_payment else None,
            last_payment_date=last_payment.paid_at.date().isoformat() if last_payment else None,
            latest_billing_month=(
                latest_reading.billing_month.isoformat() if latest_reading else None
            ),
            latest_electricity_current=(
                latest_reading.electricity_current if latest_reading else None
            ),
            latest_water_current=latest_reading.water_current if latest_reading else None,
        )

    @staticmethod
    def _build_room_code(building_code: str, room_name: str) -> str:
        return f"{building_code}-{room_name.strip()}"
