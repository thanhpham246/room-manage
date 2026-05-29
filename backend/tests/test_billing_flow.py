import httpx
import pytest


async def _create_contract(client: httpx.AsyncClient) -> int:
    building = (
        await client.post(
            "/api/v1/buildings",
            json={
                "name": "Billing House",
                "address": "99 Main",
                "default_room_rent_price": 4200000,
                "default_room_deposit_amount": 4200000,
                "default_room_area_sqm": 30,
                "floors": [{"floor_number": 2, "expected_room_count": 1}],
            },
        )
    ).json()
    room = (await client.get(f"/api/v1/rooms?building_id={building['id']}")).json()["items"][0]
    tenant = (
        await client.post(
            "/api/v1/tenants",
            json={
                "full_name": "Nguyen Van A",
                "phone": "0900000001",
                "email": "tenant@example.com",
            },
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
                "monthly_rent": 4200000,
                "deposit_amount": 4200000,
            },
        )
    ).json()
    return contract["id"]


@pytest.mark.anyio
async def test_batch_invoice_generation_calculates_totals(
    authenticated_client: httpx.AsyncClient,
) -> None:
    contract_id = await _create_contract(authenticated_client)

    response = await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "electricity_unit_price": 3500,
            "water_unit_price": 15000,
            "fixed_service_amount": 100000,
            "readings": [
                {
                    "contract_id": contract_id,
                    "electricity_previous": 100,
                    "electricity_current": 150,
                    "water_previous": 10,
                    "water_current": 14,
                    "surcharge_amount": 50000,
                    "discount_amount": 20000,
                }
            ],
        },
    )

    assert response.status_code == 201
    invoice = response.json()["items"][0]
    assert invoice["rent_amount"] == 4200000
    assert invoice["electricity_amount"] == 175000
    assert invoice["water_amount"] == 60000
    assert invoice["service_amount"] == 100000
    assert invoice["total_amount"] == 4565000
    assert invoice["status"] == "unpaid"


@pytest.mark.anyio
async def test_payment_updates_invoice_status(
    authenticated_client: httpx.AsyncClient,
) -> None:
    contract_id = await _create_contract(authenticated_client)
    invoice = (
        await authenticated_client.post(
            "/api/v1/invoices/generate",
            json={
                "billing_month": "2026-05-01",
                "electricity_unit_price": 0,
                "water_unit_price": 0,
                "fixed_service_amount": 0,
                "readings": [{"contract_id": contract_id}],
            },
        )
    ).json()["items"][0]

    partial = await authenticated_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice["id"], "amount": 1000000, "method": "cash"},
    )
    assert partial.status_code == 201
    assert partial.json()["invoice_status"] == "partial"

    remaining = invoice["total_amount"] - 1000000
    paid = await authenticated_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice["id"], "amount": remaining, "method": "bank_transfer"},
    )
    assert paid.status_code == 201
    assert paid.json()["invoice_status"] == "paid"
