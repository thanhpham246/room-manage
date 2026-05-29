from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Contract


class ContractRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, contract_id: int) -> Contract | None:
        return self.db.get(Contract, contract_id)

    def create(self, contract: Contract) -> Contract:
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def list(
        self,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Contract], int]:
        query = select(Contract)
        count_query = select(func.count()).select_from(Contract)
        if status:
            query = query.where(Contract.status == status)
            count_query = count_query.where(Contract.status == status)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Contract.id).offset(skip).limit(limit)))
        return items, total
