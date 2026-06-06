from pathlib import Path

from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController
from matheushpmoreira.vehicle_rental_system.backend.database import Database


def main() -> None:
    path = Path(".vehicle_rental.sqlite3")
    path.unlink(missing_ok=True)
    controller = AppController(Database(path))

    vehicles = [
        ("ABC1D23", "Toyota", "Corolla", 2022, "car", 180.0),
        ("MOT9A87", "Honda", "CB 500F", 2021, "motorcycle", 95.0),
        ("TRK4B56", "Ford", "Ranger", 2023, "truck", 260.0),
        ("VAN7C45", "Mercedes-Benz", "Sprinter", 2020, "van", 320.0),
    ]

    customers = [
        ("11122233344", "Ana Costa", "(11) 90000-1000", "ana@example.com", "Rua Central, 100", "ana123"),
        ("55566677788", "Bruno Lima", "(11) 90000-2000", "bruno@example.com", "Av. Norte, 250", "bruno123"),
    ]

    for plate, brand, model, year, vehicle_type, rate in vehicles:
        controller.post_vehicle(
            {
                "plate": plate,
                "brand": brand,
                "model": model,
                "year": year,
                "vehicle_type": vehicle_type,
                "daily_rate": rate,
            }
        )

    for code, name, phone, email, address, password in customers:
        controller.post_customer(
            {
                "code": code,
                "name": name,
                "phone": phone,
                "email": email,
                "address": address,
                "password": password,
            }
        )

    controller.post_rental(
        {
            "customer_code": "11122233344",
            "vehicle_plate": "ABC1D23",
            "pickup_date": "2026-05-31",
            "days": 3,
        }
    )


if __name__ == "__main__":
    main()
