from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.modules.buildings.repository import BuildingRepository
from app.modules.rooms.repository import RoomRepository
from app.modules.rooms.schemas import RoomCreate, RoomDashboard, RoomList, RoomRead, RoomUpdate
from app.modules.rooms.service import RoomService
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


def get_room_service(db: Session) -> RoomService:
    return RoomService(RoomRepository(db), BuildingRepository(db))


@router.post("", response_model=RoomRead, status_code=201)
async def create_room(payload: RoomCreate, db: Session = Depends(get_db)) -> RoomRead:
    service = get_room_service(db)
    try:
        room = service.create(payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(room)


@router.get("", response_model=RoomList)
async def list_rooms(
    building_id: int | None = None,
    floor_id: int | None = None,
    status: str | None = None,
    room_type: str | None = None,
    search: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> RoomList:
    service = get_room_service(db)
    items, total = service.list(
        building_id=building_id,
        floor_id=floor_id,
        status=status,
        room_type=room_type,
        search=search,
        skip=skip,
        limit=limit,
    )
    return RoomList(items=[service.to_read(item) for item in items], total=total)


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(room_id: int, db: Session = Depends(get_db)) -> RoomRead:
    service = get_room_service(db)
    try:
        room = service.get_or_raise(room_id)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(room)


@router.patch("/{room_id}", response_model=RoomRead)
async def update_room(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
) -> RoomRead:
    service = get_room_service(db)
    try:
        room = service.update(room_id, payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(room)


@router.get("/{room_id}/dashboard", response_model=RoomDashboard)
async def get_room_dashboard(room_id: int, db: Session = Depends(get_db)) -> RoomDashboard:
    service = get_room_service(db)
    try:
        return service.dashboard(room_id)
    except DomainError as error:
        raise_http_error(error)
