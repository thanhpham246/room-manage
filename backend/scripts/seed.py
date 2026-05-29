from datetime import date

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import (
    Building,
    BuildingAmenity,
    BuildingExpenseTemplate,
    Contract,
    Floor,
    Invoice,
    Payment,
    Room,
    Tenant,
    User,
)


def seed() -> None:
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == "admin@example.com").one_or_none()
        if admin is None:
            admin = User(
                email="admin@example.com",
                full_name="Admin User",
                hashed_password=hash_password("password123"),
                role="admin",
            )
            db.add(admin)

        staff = db.query(User).filter(User.email == "staff@example.com").one_or_none()
        if staff is None:
            staff = User(
                email="staff@example.com",
                full_name="Staff User",
                hashed_password=hash_password("password123"),
                role="staff",
            )
            db.add(staff)
            db.flush()

        building = db.query(Building).filter(Building.name == "Nguyen Trai House").one_or_none()
        if building is None:
            building = Building(
                code="HOUSE-001",
                name="Nguyen Trai House",
                address="12 Nguyen Trai",
                house_type="boarding_house",
                number_of_floors=3,
                owner_name="Demo Owner",
                owner_phone="0900000000",
                manager_id=staff.id if staff else None,
                status="active",
                phone="0280000000",
                email="nguyentrai@example.com",
                zalo="0900000000",
                emergency_contact_name="Demo Emergency",
                emergency_contact_phone="0900000009",
            )
            db.add(building)
            db.flush()
        else:
            building.code = building.code or "HOUSE-001"
            building.house_type = building.house_type or "boarding_house"
            building.number_of_floors = building.number_of_floors or 3
            building.manager_id = building.manager_id or (staff.id if staff else None)
            building.status = building.status or "active"

        floors_by_number: dict[int, Floor] = {}
        for floor_number in range(1, 4):
            floor = (
                db.query(Floor)
                .filter(Floor.building_id == building.id, Floor.floor_number == floor_number)
                .one_or_none()
            )
            if floor is None:
                floor = Floor(
                    building_id=building.id,
                    floor_number=floor_number,
                    name=f"Floor {floor_number}",
                    expected_room_count=5,
                )
                db.add(floor)
                db.flush()
            floors_by_number[floor_number] = floor

        rooms = db.query(Room).filter(Room.building_id == building.id).count()
        if rooms == 0:
            for floor_number in range(1, 4):
                for room_number in range(1, 6):
                    room_name = f"{floor_number}{room_number:02d}"
                    rent_price = 3500000 + (room_number % 3) * 300000
                    db.add(
                        Room(
                            building_id=building.id,
                            floor_id=floors_by_number[floor_number].id,
                            code=f"{building.code}-{room_name}",
                            name=room_name,
                            room_type="standard",
                            floor=floor_number,
                            area_sqm=24,
                            max_occupants=2,
                            rent_price=rent_price,
                            deposit_amount=3500000,
                            status="vacant",
                        )
                    )
            db.flush()
        else:
            for room in db.query(Room).filter(Room.building_id == building.id).all():
                if room.floor_id is None and room.floor in floors_by_number:
                    room.floor_id = floors_by_number[room.floor].id
                if not room.code:
                    room.code = f"{building.code}-{room.name}"
                room.room_type = room.room_type or "standard"
                room.max_occupants = room.max_occupants or 1
                if room.status not in {
                    "vacant",
                    "occupied",
                    "reserved",
                    "maintenance",
                    "unavailable",
                }:
                    room.status = "vacant"

        for amenity_key in ["wifi", "camera", "parking", "security"]:
            existing_amenity = (
                db.query(BuildingAmenity)
                .filter(
                    BuildingAmenity.building_id == building.id,
                    BuildingAmenity.amenity_key == amenity_key,
                )
                .one_or_none()
            )
            if existing_amenity is None:
                db.add(BuildingAmenity(building_id=building.id, amenity_key=amenity_key))

        for category, name, amount in [
            ("internet", "Wifi", 300000),
            ("security", "Security", 2000000),
            ("cleaning", "Cleaning", 500000),
        ]:
            existing_template = (
                db.query(BuildingExpenseTemplate)
                .filter(
                    BuildingExpenseTemplate.building_id == building.id,
                    BuildingExpenseTemplate.category == category,
                    BuildingExpenseTemplate.name == name,
                )
                .one_or_none()
            )
            if existing_template is None:
                db.add(
                    BuildingExpenseTemplate(
                        building_id=building.id,
                        category=category,
                        name=name,
                        default_amount=amount,
                    )
                )

        tenant = db.query(Tenant).filter(Tenant.phone == "0900000001").one_or_none()
        if tenant is None:
            tenant = Tenant(
                full_name="Nguyen Van A",
                phone="0900000001",
                email="tenant@example.com",
                emergency_contact="0900000002",
            )
            db.add(tenant)
            db.flush()

        room = db.query(Room).filter(Room.building_id == building.id).first()
        contract = db.query(Contract).filter(Contract.tenant_id == tenant.id).one_or_none()
        if room is not None and contract is None:
            room.status = "occupied"
            contract = Contract(
                room_id=room.id,
                tenant_id=tenant.id,
                start_date=date(2026, 5, 1),
                end_date=date(2027, 5, 1),
                monthly_rent=room.rent_price,
                deposit_amount=room.deposit_amount,
                status="active",
            )
            db.add(contract)
            db.flush()

        if contract is not None:
            invoice = (
                db.query(Invoice)
                .filter(
                    Invoice.contract_id == contract.id,
                    Invoice.billing_month == date(2026, 5, 1),
                )
                .one_or_none()
            )
            if invoice is None:
                invoice = Invoice(
                    contract_id=contract.id,
                    room_id=contract.room_id,
                    tenant_id=contract.tenant_id,
                    billing_month=date(2026, 5, 1),
                    rent_amount=contract.monthly_rent,
                    electricity_amount=175000,
                    water_amount=60000,
                    service_amount=100000,
                    total_amount=contract.monthly_rent + 335000,
                    paid_amount=1000000,
                    status="partial",
                )
                db.add(invoice)
                db.flush()
                db.add(Payment(invoice_id=invoice.id, amount=1000000, method="cash"))

        db.commit()


if __name__ == "__main__":
    seed()
