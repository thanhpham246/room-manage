from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.routers._errors import raise_http_error
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.modules.buildings.repository import BuildingRepository
from app.modules.buildings.schemas import (
    BuildingCreate,
    BuildingDashboard,
    BuildingList,
    BuildingRead,
    BuildingTree,
    BuildingUpdate,
)
from app.modules.buildings.service import BuildingService
from app.repositories.users import UserRepository
from app.services.errors import DomainError

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


def get_building_service(db: Session) -> BuildingService:
    return BuildingService(BuildingRepository(db), UserRepository(db))


@router.post("", response_model=BuildingRead, status_code=201)
async def create_building(payload: BuildingCreate, db: Session = Depends(get_db)) -> BuildingRead:
    service = get_building_service(db)
    try:
        building = service.create(payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(building)


@router.get("", response_model=BuildingList)
async def list_buildings(
    search: str | None = None,
    house_type: str | None = None,
    status: str | None = None,
    manager_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> BuildingList:
    service = get_building_service(db)
    items, total = service.list(
        search=search,
        house_type=house_type,
        status=status,
        manager_id=manager_id,
        skip=skip,
        limit=limit,
    )
    return BuildingList(items=[service.to_read(item) for item in items], total=total)


@router.get("/{building_id}", response_model=BuildingRead)
async def get_building(building_id: int, db: Session = Depends(get_db)) -> BuildingRead:
    service = get_building_service(db)
    try:
        building = service.get_or_raise(building_id)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(building)


@router.patch("/{building_id}", response_model=BuildingRead)
async def update_building(
    building_id: int,
    payload: BuildingUpdate,
    db: Session = Depends(get_db),
) -> BuildingRead:
    service = get_building_service(db)
    try:
        building = service.update(building_id, payload)
    except DomainError as error:
        raise_http_error(error)
    return service.to_read(building)


@router.get("/{building_id}/dashboard", response_model=BuildingDashboard)
async def get_building_dashboard(
    building_id: int,
    month: str | None = None,
    db: Session = Depends(get_db),
) -> BuildingDashboard:
    service = get_building_service(db)
    try:
        dashboard_month = parse_month(month)
        return service.dashboard(building_id, dashboard_month)
    except DomainError as error:
        raise_http_error(error)


@router.get("/{building_id}/tree", response_model=BuildingTree)
async def get_building_tree(building_id: int, db: Session = Depends(get_db)) -> BuildingTree:
    service = get_building_service(db)
    try:
        return service.tree(building_id)
    except DomainError as error:
        raise_http_error(error)


def parse_month(month: str | None) -> date:
    if month is None:
        return date.today().replace(day=1)
    try:
        year, month_number = month.split("-", maxsplit=1)
        return date(int(year), int(month_number), 1)
    except ValueError as error:
        raise HTTPException(status_code=422, detail="Month must use YYYY-MM format") from error
