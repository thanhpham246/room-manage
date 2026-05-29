from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Contract, Expense, Invoice, Room
from app.schemas.dashboard import CashFlowPoint, DashboardKpi, DashboardSummary


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self) -> DashboardSummary:
        today = date.today()
        first_day = today.replace(day=1)
        total_rooms = self.db.scalar(select(func.count()).select_from(Room)) or 0
        occupied_rooms = self.db.scalar(
            select(func.count()).select_from(Room).where(Room.status == "occupied")
        ) or 0
        vacant_rooms = self.db.scalar(
            select(func.count()).select_from(Room).where(Room.status == "vacant")
        ) or 0
        monthly_revenue = self.db.scalar(
            select(func.coalesce(func.sum(Invoice.paid_amount), 0)).where(
                Invoice.billing_month == first_day
            )
        ) or 0
        outstanding_amount = self.db.scalar(
            select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)).where(
                Invoice.status != "paid"
            )
        ) or 0
        expiring_contracts = self.db.scalar(
            select(func.count()).select_from(Contract).where(Contract.status == "active")
        ) or 0
        expenses = self.db.scalar(select(func.coalesce(func.sum(Expense.amount), 0))) or 0
        cash_flow = [
            CashFlowPoint(
                month=first_day.strftime("%Y-%m"),
                revenue=monthly_revenue,
                expenses=expenses,
                profit=monthly_revenue - expenses,
            )
        ]
        return DashboardSummary(
            kpi=DashboardKpi(
                monthly_revenue=monthly_revenue,
                occupied_rooms=occupied_rooms,
                total_rooms=total_rooms,
                vacant_rooms=vacant_rooms,
                expiring_contracts=expiring_contracts,
                outstanding_amount=outstanding_amount,
            ),
            cash_flow=cash_flow,
        )
