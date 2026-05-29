import httpx
import pytest


async def create_contract(client: httpx.AsyncClient) -> int:
    building = (
        await client.post(
            "/api/v1/buildings",
            json={
                "name": "Coverage House",
                "address": "1 Test",
                "default_room_rent_price": 3900000,
                "default_room_deposit_amount": 3900000,
                "floors": [{"floor_number": 3, "expected_room_count": 1}],
            },
        )
    ).json()
    room = (await client.get(f"/api/v1/rooms?building_id={building['id']}")).json()["items"][0]
    tenant = (
        await client.post(
            "/api/v1/tenants",
            json={"full_name": "Tran Thi B", "phone": "0900000003"},
        )
    ).json()
    contract = (
        await client.post(
            "/api/v1/contracts",
            json={
                "room_id": room["id"],
                "tenant_id": tenant["id"],
                "start_date": "2026-05-01",
                "end_date": "2027-05-01",
                "monthly_rent": 3900000,
                "deposit_amount": 3900000,
            },
        )
    ).json()
    return contract["id"]


@pytest.mark.anyio
async def test_admin_can_create_user_and_list_users(
    authenticated_client: httpx.AsyncClient,
) -> None:
    created = await authenticated_client.post(
        "/api/v1/users",
        json={
            "email": "staff2@example.com",
            "full_name": "Staff Two",
            "password": "password123",
            "role": "staff",
        },
    )
    assert created.status_code == 201

    users = await authenticated_client.get("/api/v1/users")

    assert users.status_code == 200
    assert any(user["email"] == "staff2@example.com" for user in users.json())


@pytest.mark.anyio
async def test_expenses_and_dashboard_summary(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building = (
        await authenticated_client.post(
            "/api/v1/buildings",
            json={"name": "Expense House", "address": "2 Test"},
        )
    ).json()
    expense = await authenticated_client.post(
        "/api/v1/expenses",
        json={
            "building_id": building["id"],
            "category": "repair",
            "amount": 250000,
            "spent_on": "2026-05-02",
        },
    )
    assert expense.status_code == 201

    expenses = await authenticated_client.get(f"/api/v1/expenses?building_id={building['id']}")
    dashboard = await authenticated_client.get("/api/v1/dashboard/summary")

    assert expenses.status_code == 200
    assert expenses.json()["total"] == 1
    assert dashboard.status_code == 200
    assert "kpi" in dashboard.json()


@pytest.mark.anyio
async def test_list_endpoints_return_paginated_payloads(
    authenticated_client: httpx.AsyncClient,
) -> None:
    contract_id = await create_contract(authenticated_client)
    await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "readings": [{"contract_id": contract_id}],
        },
    )

    for path in [
        "/api/v1/buildings",
        "/api/v1/tenants",
        "/api/v1/contracts",
        "/api/v1/invoices",
        "/api/v1/payments",
    ]:
        response = await authenticated_client.get(path)
        assert response.status_code == 200
        assert "items" in response.json()
        assert "total" in response.json()


@pytest.mark.anyio
async def test_domain_error_paths(authenticated_client: httpx.AsyncClient) -> None:
    missing_building_room = await authenticated_client.post(
        "/api/v1/rooms",
        json={
            "building_id": 999,
            "name": "404",
            "rent_price": 1000000,
            "deposit_amount": 1000000,
        },
    )
    assert missing_building_room.status_code == 404

    contract_id = await create_contract(authenticated_client)
    first_invoice = await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "readings": [{"contract_id": contract_id}],
        },
    )
    duplicate_invoice = await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "readings": [{"contract_id": contract_id}],
        },
    )
    assert first_invoice.status_code == 201
    assert duplicate_invoice.status_code == 409

    invoice = first_invoice.json()["items"][0]
    overpay = await authenticated_client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice["id"],
            "amount": invoice["total_amount"] + 1,
            "method": "cash",
        },
    )
    assert overpay.status_code == 409
