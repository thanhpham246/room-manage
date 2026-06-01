from fastapi import APIRouter

from app.api.v1.routers import (
    auth,
    contracts,
    dashboard,
    expenses,
    invoices,
    payments,
    tenants,
    users,
)
from app.modules.buildings.router import router as buildings_router
from app.modules.rooms.router import router as rooms_router

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
async def api_health() -> dict[str, str]:
    return {"status": "ok", "api": "v1"}


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(buildings_router, prefix="/buildings", tags=["buildings"])
api_router.include_router(rooms_router, prefix="/rooms", tags=["rooms"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
