from sqlalchemy.orm import Session

from app.models import Contract
from app.repositories.contracts import ContractRepository
from app.repositories.properties import RoomRepository
from app.repositories.tenants import TenantRepository
from app.schemas.contracts import ContractCreate
from app.services.errors import ConflictError, NotFoundError


class ContractService:
    def __init__(
        self,
        db: Session,
        contracts: ContractRepository,
        rooms: RoomRepository,
        tenants: TenantRepository,
    ) -> None:
        self.db = db
        self.contracts = contracts
        self.rooms = rooms
        self.tenants = tenants

    def create(self, payload: ContractCreate) -> Contract:
        room = self.rooms.get(payload.room_id)
        if room is None:
            raise NotFoundError("Room not found")
        if room.status != "vacant":
            raise ConflictError("Room is not vacant")
        if self.tenants.get(payload.tenant_id) is None:
            raise NotFoundError("Tenant not found")

        contract = Contract(**payload.model_dump(), status="active")
        self.db.add(contract)
        room.status = "occupied"
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def list(self, status: str | None, skip: int, limit: int) -> tuple[list[Contract], int]:
        return self.contracts.list(status=status, skip=skip, limit=limit)
