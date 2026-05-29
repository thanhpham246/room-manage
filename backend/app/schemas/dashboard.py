from pydantic import BaseModel


class DashboardKpi(BaseModel):
    monthly_revenue: int
    occupied_rooms: int
    total_rooms: int
    vacant_rooms: int
    expiring_contracts: int
    outstanding_amount: int


class CashFlowPoint(BaseModel):
    month: str
    revenue: int
    expenses: int
    profit: int


class DashboardSummary(BaseModel):
    kpi: DashboardKpi
    cash_flow: list[CashFlowPoint]
