import httpx
import pytest


@pytest.mark.anyio
async def test_tenant_profile_search_update_and_soft_delete(
    authenticated_client: httpx.AsyncClient,
) -> None:
    create_response = await authenticated_client.post(
        "/api/v1/tenants",
        json={
            "full_name": "Le Van A",
            "phone": "0900001001",
            "email": "tenant-a@example.com",
            "zalo": "0900001001",
            "date_of_birth": "1995-01-20",
            "gender": "male",
            "identity_type": "cccd",
            "identity_number": "079095001001",
            "identity_issued_date": "2021-03-15",
            "identity_issued_place": "Ho Chi Minh City Police",
            "permanent_address": "1 Nguyen Trai",
            "current_address": "2 Nguyen Trai",
            "emergency_contact_name": "Le Thi B",
            "emergency_contact_phone": "0900001002",
            "emergency_contact_relationship": "Sibling",
            "note": "Prefers SMS reminders",
        },
    )

    assert create_response.status_code == 201
    tenant = create_response.json()
    assert tenant["tenant_code"] == "TENANT-001"
    assert tenant["status"] == "not_renting"
    assert tenant["identity_edit_warning"] is False

    duplicate_response = await authenticated_client.post(
        "/api/v1/tenants",
        json={
            "full_name": "Duplicate Identity",
            "phone": "0900001003",
            "identity_number": "079095001001",
        },
    )
    assert duplicate_response.status_code == 409

    search_response = await authenticated_client.get(
        "/api/v1/tenants",
        params={"search": "  le   van  ", "status": "not_renting"},
    )
    assert search_response.status_code == 200
    assert search_response.json()["total"] == 1
    assert search_response.json()["items"][0]["tenant_code"] == "TENANT-001"

    update_response = await authenticated_client.patch(
        f"/api/v1/tenants/{tenant['id']}",
        json={"identity_number": "079095001999", "phone": "0900001999"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["tenant_code"] == "TENANT-001"
    assert update_response.json()["identity_number"] == "079095001999"
    assert update_response.json()["identity_edit_warning"] is False

    delete_response = await authenticated_client.delete(f"/api/v1/tenants/{tenant['id']}")
    assert delete_response.status_code == 204

    default_list_response = await authenticated_client.get("/api/v1/tenants")
    assert default_list_response.status_code == 200
    assert default_list_response.json()["total"] == 0

    deleted_list_response = await authenticated_client.get(
        "/api/v1/tenants",
        params={"status": "deleted"},
    )
    assert deleted_list_response.status_code == 200
    assert deleted_list_response.json()["total"] == 1
    assert deleted_list_response.json()["items"][0]["status"] == "deleted"

    reuse_identity_response = await authenticated_client.post(
        "/api/v1/tenants",
        json={
            "full_name": "Reuse Identity",
            "phone": "0900001004",
            "identity_number": "079095001999",
        },
    )
    assert reuse_identity_response.status_code == 201
    assert reuse_identity_response.json()["tenant_code"] == "TENANT-002"


@pytest.mark.anyio
async def test_active_tenant_detail_identity_warning_and_contract_rejects_deleted_tenant(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building_response = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-901",
            "name": "Tenant Detail House",
            "address": "901 Test",
            "default_room_rent_price": 3200000,
            "default_room_deposit_amount": 3200000,
            "floors": [{"floor_number": 1, "expected_room_count": 2}],
        },
    )
    assert building_response.status_code == 201
    building = building_response.json()
    rooms_response = await authenticated_client.get(f"/api/v1/rooms?building_id={building['id']}")
    rooms = rooms_response.json()["items"]

    tenant_response = await authenticated_client.post(
        "/api/v1/tenants",
        json={
            "full_name": "Active Tenant",
            "phone": "0900001901",
            "identity_number": "079095001901",
        },
    )
    assert tenant_response.status_code == 201
    tenant = tenant_response.json()

    contract_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "room_id": rooms[0]["id"],
            "tenant_id": tenant["id"],
            "start_date": "2026-05-01",
            "end_date": "2027-05-01",
            "monthly_rent": 3200000,
            "deposit_amount": 3200000,
        },
    )
    assert contract_response.status_code == 201

    update_response = await authenticated_client.patch(
        f"/api/v1/tenants/{tenant['id']}",
        json={"identity_number": "079095001902"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["identity_number"] == "079095001902"
    assert update_response.json()["identity_edit_warning"] is True

    detail_response = await authenticated_client.get(f"/api/v1/tenants/{tenant['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["status"] == "active"
    assert detail["current_building_name"] == "Tenant Detail House"
    assert detail["current_room_code"] == rooms[0]["code"]
    assert detail["active_contract_id"] == contract_response.json()["id"]
    assert detail["deposit_amount"] == 3200000

    delete_response = await authenticated_client.delete(f"/api/v1/tenants/{tenant['id']}")
    assert delete_response.status_code == 204

    deleted_contract_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "room_id": rooms[1]["id"],
            "tenant_id": tenant["id"],
            "start_date": "2026-06-01",
            "end_date": "2027-06-01",
            "monthly_rent": 3200000,
            "deposit_amount": 3200000,
        },
    )
    assert deleted_contract_response.status_code == 404
