import httpx
import pytest


async def create_building_with_rooms(
    client: httpx.AsyncClient,
    *,
    code: str,
    room_count: int = 2,
) -> dict:
    response = await client.post(
        "/api/v1/buildings",
        json={
            "code": code,
            "name": f"{code} House",
            "address": "1 Contract Test",
            "default_room_rent_price": 3000000,
            "default_room_deposit_amount": 3000000,
            "floors": [{"floor_number": 1, "expected_room_count": room_count}],
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_tenant(
    client: httpx.AsyncClient,
    *,
    phone: str,
    name: str = "Contract Tenant",
) -> dict:
    response = await client.post(
        "/api/v1/tenants",
        json={"full_name": name, "phone": phone},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.anyio
async def test_room_contract_generates_code_reserves_future_room_and_blocks_overlap(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building = await create_building_with_rooms(authenticated_client, code="HOUSE-1201")
    rooms = (
        await authenticated_client.get(f"/api/v1/rooms?building_id={building['id']}")
    ).json()["items"]
    tenant = await create_tenant(authenticated_client, phone="0900012010")
    second_tenant = await create_tenant(
        authenticated_client,
        phone="0900012011",
        name="Overlap Tenant",
    )

    contract_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "scope": "room",
            "room_id": rooms[0]["id"],
            "tenant_id": tenant["id"],
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "monthly_rent": 3000000,
            "deposit_amount": 3000000,
        },
    )

    assert contract_response.status_code == 201
    contract = contract_response.json()
    assert contract["contract_code"] == "CONTRACT-001"
    assert contract["scope"] == "room"
    assert contract["building_id"] == building["id"]
    assert contract["room_id"] == rooms[0]["id"]
    assert contract["status"] == "pending"

    room_response = await authenticated_client.get(f"/api/v1/rooms/{rooms[0]['id']}")
    assert room_response.status_code == 200
    assert room_response.json()["status"] == "reserved"

    overlap_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "scope": "room",
            "room_id": rooms[0]["id"],
            "tenant_id": second_tenant["id"],
            "start_date": "2026-08-01",
            "end_date": "2027-01-31",
            "monthly_rent": 3100000,
            "deposit_amount": 3100000,
        },
    )
    adjacent_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "scope": "room",
            "room_id": rooms[0]["id"],
            "tenant_id": second_tenant["id"],
            "start_date": "2027-01-01",
            "end_date": "2027-06-30",
            "monthly_rent": 3100000,
            "deposit_amount": 3100000,
        },
    )

    assert overlap_response.status_code == 409
    assert adjacent_response.status_code == 201
    assert adjacent_response.json()["contract_code"] == "CONTRACT-002"


@pytest.mark.anyio
async def test_whole_building_contract_blocks_building_overlap_and_generates_invoice(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building = await create_building_with_rooms(authenticated_client, code="HOUSE-1202")
    rooms = (
        await authenticated_client.get(f"/api/v1/rooms?building_id={building['id']}")
    ).json()["items"]
    room_tenant = await create_tenant(authenticated_client, phone="0900012020")
    building_tenant = await create_tenant(
        authenticated_client,
        phone="0900012021",
        name="Whole Building Tenant",
    )

    room_contract_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "scope": "room",
            "room_id": rooms[0]["id"],
            "tenant_id": room_tenant["id"],
            "start_date": "2026-05-01",
            "end_date": "2026-06-30",
            "monthly_rent": 3000000,
            "deposit_amount": 3000000,
        },
    )
    assert room_contract_response.status_code == 201

    overlap_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "scope": "whole_building",
            "building_id": building["id"],
            "tenant_id": building_tenant["id"],
            "start_date": "2026-06-01",
            "end_date": "2026-12-31",
            "monthly_rent": 15000000,
            "deposit_amount": 15000000,
        },
    )
    assert overlap_response.status_code == 409

    whole_building_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "scope": "whole_building",
            "building_id": building["id"],
            "tenant_id": building_tenant["id"],
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "monthly_rent": 15000000,
            "deposit_amount": 15000000,
        },
    )
    assert whole_building_response.status_code == 201
    whole_building_contract = whole_building_response.json()
    assert whole_building_contract["scope"] == "whole_building"
    assert whole_building_contract["building_id"] == building["id"]
    assert whole_building_contract["room_id"] is None
    assert whole_building_contract["status"] == "pending"

    billing_building = await create_building_with_rooms(
        authenticated_client,
        code="HOUSE-1202-BILLING",
    )
    active_whole_building_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "scope": "whole_building",
            "building_id": billing_building["id"],
            "tenant_id": building_tenant["id"],
            "start_date": "2026-05-01",
            "end_date": "2026-12-31",
            "monthly_rent": 12000000,
            "deposit_amount": 12000000,
        },
    )
    assert active_whole_building_response.status_code == 201
    active_contract = active_whole_building_response.json()
    assert active_contract["status"] == "active"

    invoice_response = await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "electricity_unit_price": 4000,
            "water_unit_price": 10000,
            "fixed_service_amount": 500000,
            "readings": [
                {
                    "contract_id": active_contract["id"],
                    "electricity_previous": 10,
                    "electricity_current": 20,
                    "water_previous": 2,
                    "water_current": 5,
                }
            ],
        },
    )
    assert invoice_response.status_code == 201
    invoice = invoice_response.json()["items"][0]
    assert invoice["building_id"] == billing_building["id"]
    assert invoice["room_id"] is None
    assert invoice["tenant_id"] == building_tenant["id"]
    assert invoice["total_amount"] == 12570000


@pytest.mark.anyio
async def test_contract_monthly_rent_is_locked_after_invoice_exists(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building = await create_building_with_rooms(
        authenticated_client,
        code="HOUSE-1203",
        room_count=1,
    )
    room = (await authenticated_client.get(f"/api/v1/rooms?building_id={building['id']}")).json()[
        "items"
    ][0]
    tenant = await create_tenant(authenticated_client, phone="0900012030")
    contract_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "room_id": room["id"],
            "tenant_id": tenant["id"],
            "start_date": "2026-05-01",
            "end_date": "2026-12-31",
            "monthly_rent": 3300000,
            "deposit_amount": 3300000,
        },
    )
    assert contract_response.status_code == 201
    contract = contract_response.json()

    invoice_response = await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "readings": [{"contract_id": contract["id"]}],
        },
    )
    assert invoice_response.status_code == 201

    rent_update_response = await authenticated_client.patch(
        f"/api/v1/contracts/{contract['id']}",
        json={"monthly_rent": 3500000},
    )
    note_update_response = await authenticated_client.patch(
        f"/api/v1/contracts/{contract['id']}",
        json={"note": "Updated note after invoice"},
    )

    assert rent_update_response.status_code == 409
    assert note_update_response.status_code == 200
    assert note_update_response.json()["monthly_rent"] == 3300000
    assert note_update_response.json()["note"] == "Updated note after invoice"


@pytest.mark.anyio
async def test_contract_detail_search_update_before_invoice_and_soft_delete(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building = await create_building_with_rooms(
        authenticated_client,
        code="HOUSE-1204",
        room_count=2,
    )
    rooms = (await authenticated_client.get(f"/api/v1/rooms?building_id={building['id']}")).json()[
        "items"
    ]
    tenant = await create_tenant(authenticated_client, phone="0900012040")
    next_tenant = await create_tenant(
        authenticated_client,
        phone="0900012041",
        name="Next Contract Tenant",
    )
    create_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "room_id": rooms[0]["id"],
            "tenant_id": tenant["id"],
            "start_date": "2026-05-01",
            "end_date": "2026-12-31",
            "monthly_rent": 3400000,
            "deposit_amount": 3400000,
        },
    )
    assert create_response.status_code == 201
    contract = create_response.json()

    search_response = await authenticated_client.get(
        "/api/v1/contracts",
        params={"search": "  contract-001  ", "status": "active"},
    )
    detail_response = await authenticated_client.get(f"/api/v1/contracts/{contract['id']}")
    update_response = await authenticated_client.patch(
        f"/api/v1/contracts/{contract['id']}",
        json={
            "room_id": rooms[1]["id"],
            "tenant_id": next_tenant["id"],
            "monthly_rent": 3600000,
            "deposit_amount": 3600000,
            "note": "Moved before invoice",
        },
    )

    assert search_response.status_code == 200
    assert search_response.json()["total"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["contract_code"] == "CONTRACT-001"
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["room_id"] == rooms[1]["id"]
    assert updated["tenant_id"] == next_tenant["id"]
    assert updated["monthly_rent"] == 3600000
    assert updated["note"] == "Moved before invoice"

    old_room_response = await authenticated_client.get(f"/api/v1/rooms/{rooms[0]['id']}")
    new_room_response = await authenticated_client.get(f"/api/v1/rooms/{rooms[1]['id']}")
    assert old_room_response.json()["status"] == "vacant"
    assert new_room_response.json()["status"] == "occupied"

    delete_response = await authenticated_client.delete(f"/api/v1/contracts/{contract['id']}")
    deleted_list_response = await authenticated_client.get(
        "/api/v1/contracts",
        params={"status": "deleted"},
    )

    assert delete_response.status_code == 204
    assert deleted_list_response.status_code == 200
    assert deleted_list_response.json()["total"] == 1
    assert deleted_list_response.json()["items"][0]["status"] == "deleted"
