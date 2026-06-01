from __future__ import annotations

from app.models import Room
from app.modules.buildings.repository import BuildingRepository
from app.modules.rooms.repository import RoomRepository
from app.modules.rooms.schemas import RoomCreate, RoomDashboard, RoomRead, RoomUpdate
from app.services.errors import ConflictError, DomainError, NotFoundError


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
