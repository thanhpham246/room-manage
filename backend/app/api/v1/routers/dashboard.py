from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter(dependencies=[Depends(require_roles("admin", "staff"))])


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    return DashboardService(db).summary()
