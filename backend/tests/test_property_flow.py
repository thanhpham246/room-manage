import httpx
import pytest


async def create_staff_user(authenticated_client: httpx.AsyncClient) -> int:
    response = await authenticated_client.post(
        "/api/v1/users",
        json={
            "email": "manager@example.com",
            "full_name": "Building Manager",
            "password": "password123",
            "role": "staff",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.anyio
async def test_room_crud_supports_building_filter(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building_response = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-101",
            "name": "Nguyen Trai House",
            "address": "12 Nguyen Trai",
            "default_room_rent_price": 3500000,
            "default_room_deposit_amount": 3500000,
            "floors": [{"floor_number": 1, "expected_room_count": 1}],
        },
    )
    assert building_response.status_code == 201
    building_id = building_response.json()["id"]
    tree_response = await authenticated_client.get(f"/api/v1/buildings/{building_id}/tree")
    assert tree_response.status_code == 200
    floor_id = tree_response.json()["floors"][0]["id"]

    room_response = await authenticated_client.post(
        "/api/v1/rooms",
        json={
            "building_id": building_id,
            "floor_id": floor_id,
            "name": "102",
            "area_sqm": 24,
            "rent_price": 3500000,
            "deposit_amount": 3500000,
            "status": "vacant",
            "room_type": "studio",
            "max_occupants": 2,
        },
    )
    assert room_response.status_code == 201
    assert room_response.json()["status"] == "vacant"
    assert room_response.json()["code"] == "HOUSE-101-102"

    list_response = await authenticated_client.get(f"/api/v1/rooms?building_id={building_id}")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 2
    assert {item["name"] for item in list_response.json()["items"]} == {"101", "102"}


@pytest.mark.anyio
async def test_building_create_generates_floors_rooms_amenities_and_templates(
    authenticated_client: httpx.AsyncClient,
) -> None:
    manager_id = await create_staff_user(authenticated_client)

    response = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-777",
            "name": "Uneven House",
            "address": "77 Nguyen Hue",
            "house_type": "mini_apartment",
            "status": "active",
            "owner_name": "Owner Text",
            "owner_phone": "0900000777",
            "manager_id": manager_id,
            "phone": "028777777",
            "email": "house@example.com",
            "zalo": "0900000777",
            "emergency_contact_name": "Emergency Person",
            "emergency_contact_phone": "0900000888",
            "default_room_rent_price": 2500000,
            "default_room_deposit_amount": 2500000,
            "default_room_area_sqm": 22,
            "floors": [
                {"floor_number": 1, "name": "Floor 1", "expected_room_count": 2},
                {"floor_number": 2, "name": "Floor 2", "expected_room_count": 3},
            ],
            "amenities": ["wifi", "camera", "parking"],
            "expense_templates": [
                {"category": "internet", "name": "Wifi", "default_amount": 300000},
                {"category": "security", "name": "Security", "default_amount": 2000000},
            ],
        },
    )

    assert response.status_code == 201
    building = response.json()
    assert building["code"] == "HOUSE-777"
    assert building["manager_id"] == manager_id
    assert building["expected_rooms"] == 5
    assert building["total_rooms"] == 5
    assert set(building["amenities"]) == {"wifi", "camera", "parking"}
    assert [template["name"] for template in building["expense_templates"]] == [
        "Wifi",
        "Security",
    ]

    tree_response = await authenticated_client.get(f"/api/v1/buildings/{building['id']}/tree")

    assert tree_response.status_code == 200
    floors = tree_response.json()["floors"]
    assert [floor["expected_room_count"] for floor in floors] == [2, 3]
    assert [room["name"] for room in floors[0]["rooms"]] == ["101", "102"]
    assert [room["code"] for room in floors[0]["rooms"]] == ["HOUSE-777-101", "HOUSE-777-102"]
    assert [room["name"] for room in floors[1]["rooms"]] == ["201", "202", "203"]


@pytest.mark.anyio
async def test_building_dashboard_uses_building_scoped_metrics(
    authenticated_client: httpx.AsyncClient,
) -> None:
    manager_id = await create_staff_user(authenticated_client)
    building_response = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-778",
            "name": "Dashboard House",
            "address": "778 Le Loi",
            "manager_id": manager_id,
            "default_room_rent_price": 3000000,
            "default_room_deposit_amount": 3000000,
            "floors": [{"floor_number": 1, "expected_room_count": 2}],
        },
    )
    assert building_response.status_code == 201
    building_id = building_response.json()["id"]

    tenant_response = await authenticated_client.post(
        "/api/v1/tenants",
        json={"full_name": "Dashboard Tenant", "phone": "0900000778"},
    )
    assert tenant_response.status_code == 201

    rooms_response = await authenticated_client.get(f"/api/v1/rooms?building_id={building_id}")
    assert rooms_response.status_code == 200
    room_id = rooms_response.json()["items"][0]["id"]

    contract_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "room_id": room_id,
            "tenant_id": tenant_response.json()["id"],
            "start_date": "2026-05-01",
            "end_date": "2026-06-15",
            "monthly_rent": 3000000,
            "deposit_amount": 3000000,
        },
    )
    assert contract_response.status_code == 201

    invoice_response = await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "electricity_unit_price": 4000,
            "water_unit_price": 10000,
            "fixed_service_amount": 100000,
            "readings": [
                {
                    "contract_id": contract_response.json()["id"],
                    "electricity_previous": 10,
                    "electricity_current": 20,
                    "water_previous": 1,
                    "water_current": 3,
                }
            ],
        },
    )
    assert invoice_response.status_code == 201
    total_amount = invoice_response.json()["items"][0]["total_amount"]

    payment_response = await authenticated_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_response.json()["items"][0]["id"], "amount": 1000000},
    )
    assert payment_response.status_code == 201

    dashboard_response = await authenticated_client.get(
        f"/api/v1/buildings/{building_id}/dashboard?month=2026-05"
    )

    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["total_rooms"] == 2
    assert dashboard["occupied_rooms"] == 1
    assert dashboard["vacant_rooms"] == 1
    assert dashboard["occupancy_rate"] == 50
    assert dashboard["monthly_revenue"] == 1000000
    assert dashboard["debt"] == total_amount - 1000000
    assert dashboard["expiring_contracts"] == 1


@pytest.mark.anyio
async def test_building_rejects_non_staff_manager(
    authenticated_client: httpx.AsyncClient,
) -> None:
    admin_response = await authenticated_client.get("/api/v1/users")
    assert admin_response.status_code == 200
    admin_id = admin_response.json()[0]["id"]

    response = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-779",
            "name": "Invalid Manager House",
            "address": "779 Tran Hung Dao",
            "manager_id": admin_id,
        },
    )

    assert response.status_code == 400


@pytest.mark.anyio
async def test_building_update_replaces_metadata_amenities_and_templates(
    authenticated_client: httpx.AsyncClient,
) -> None:
    manager_id = await create_staff_user(authenticated_client)
    create_response = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-780",
            "name": "Editable House",
            "address": "780 Pasteur",
            "manager_id": manager_id,
            "amenities": ["wifi", "parking"],
            "expense_templates": [
                {"category": "internet", "name": "Wifi", "default_amount": 300000}
            ],
        },
    )
    assert create_response.status_code == 201
    building_id = create_response.json()["id"]

    update_response = await authenticated_client.patch(
        f"/api/v1/buildings/{building_id}",
        json={
            "name": "Edited House",
            "status": "under_renovation",
            "phone": "0280780780",
            "amenities": ["camera", "security"],
            "expense_templates": [
                {"category": "security", "name": "Security", "default_amount": 2000000}
            ],
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["name"] == "Edited House"
    assert body["status"] == "under_renovation"
    assert body["phone"] == "0280780780"
    assert set(body["amenities"]) == {"camera", "security"}
    assert [template["name"] for template in body["expense_templates"]] == ["Security"]

    list_response = await authenticated_client.get(
        "/api/v1/buildings?search=Edited&status=under_renovation"
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1


@pytest.mark.anyio
async def test_room_update_refreshes_code_and_detail_dashboard(
    authenticated_client: httpx.AsyncClient,
) -> None:
    building_response = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-881",
            "name": "Room Detail House",
            "address": "881 Test",
            "default_room_rent_price": 3100000,
            "default_room_deposit_amount": 3100000,
            "floors": [{"floor_number": 1, "expected_room_count": 1}],
        },
    )
    assert building_response.status_code == 201
    building_id = building_response.json()["id"]
    rooms_response = await authenticated_client.get(f"/api/v1/rooms?building_id={building_id}")
    room = rooms_response.json()["items"][0]
    assert room["code"] == "HOUSE-881-101"

    update_response = await authenticated_client.patch(
        f"/api/v1/rooms/{room['id']}",
        json={
            "name": "A1",
            "room_type": "loft",
            "max_occupants": 3,
            "status": "reserved",
            "rent_price": 3300000,
            "deposit_amount": 3300000,
            "note": "Corner room",
        },
    )
    assert update_response.status_code == 200
    updated_room = update_response.json()
    assert updated_room["code"] == "HOUSE-881-A1"
    assert updated_room["room_type"] == "loft"
    assert updated_room["max_occupants"] == 3
    assert updated_room["status"] == "reserved"

    available_response = await authenticated_client.patch(
        f"/api/v1/rooms/{room['id']}",
        json={"status": "vacant"},
    )
    assert available_response.status_code == 200

    tenant_response = await authenticated_client.post(
        "/api/v1/tenants",
        json={"full_name": "Room Tenant", "phone": "0900000881"},
    )
    assert tenant_response.status_code == 201
    contract_response = await authenticated_client.post(
        "/api/v1/contracts",
        json={
            "room_id": room["id"],
            "tenant_id": tenant_response.json()["id"],
            "start_date": "2026-05-01",
            "end_date": "2027-05-01",
            "monthly_rent": 3300000,
            "deposit_amount": 3300000,
        },
    )
    assert contract_response.status_code == 201
    invoice_response = await authenticated_client.post(
        "/api/v1/invoices/generate",
        json={
            "billing_month": "2026-05-01",
            "electricity_unit_price": 4000,
            "water_unit_price": 10000,
            "fixed_service_amount": 100000,
            "readings": [
                {
                    "contract_id": contract_response.json()["id"],
                    "electricity_previous": 10,
                    "electricity_current": 15,
                    "water_previous": 2,
                    "water_current": 4,
                }
            ],
        },
    )
    assert invoice_response.status_code == 201
    await authenticated_client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_response.json()["items"][0]["id"], "amount": 1000000},
    )

    dashboard_response = await authenticated_client.get(f"/api/v1/rooms/{room['id']}/dashboard")

    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["room"]["code"] == "HOUSE-881-A1"
    assert dashboard["tenant_name"] == "Room Tenant"
    assert dashboard["active_contract_id"] == contract_response.json()["id"]
    expected_debt = invoice_response.json()["items"][0]["total_amount"] - 1000000
    assert dashboard["current_debt"] == expected_debt
    assert dashboard["last_payment_amount"] == 1000000
    assert dashboard["latest_electricity_current"] == 15
    assert dashboard["latest_water_current"] == 4


@pytest.mark.anyio
async def test_room_create_requires_floor_belonging_to_building(
    authenticated_client: httpx.AsyncClient,
) -> None:
    first_building = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-882",
            "name": "First Room House",
            "address": "882 Test",
            "default_room_rent_price": 2000000,
            "floors": [{"floor_number": 1, "expected_room_count": 1}],
        },
    )
    second_building = await authenticated_client.post(
        "/api/v1/buildings",
        json={
            "code": "HOUSE-883",
            "name": "Second Room House",
            "address": "883 Test",
            "default_room_rent_price": 2000000,
            "floors": [{"floor_number": 1, "expected_room_count": 1}],
        },
    )
    assert first_building.status_code == 201
    assert second_building.status_code == 201
    second_tree = await authenticated_client.get(
        f"/api/v1/buildings/{second_building.json()['id']}/tree"
    )
    second_floor_id = second_tree.json()["floors"][0]["id"]

    response = await authenticated_client.post(
        "/api/v1/rooms",
        json={
            "building_id": first_building.json()["id"],
            "floor_id": second_floor_id,
            "name": "199",
            "rent_price": 2000000,
        },
    )

    assert response.status_code == 404
