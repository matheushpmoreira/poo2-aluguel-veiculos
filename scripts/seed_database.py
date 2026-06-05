from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.backend.controllers import AppController


def seed(reset: bool = False, database_path: str | Path | None = None) -> None:
    path = Path(database_path) if database_path else Path(".data") / "vehicle_rental.sqlite3"
    if reset and path.exists():
        path.unlink()

    controller = AppController(path)
    vehicles = [
        ("ABC1D23", "Toyota", "Corolla", 2022, "car", 180.0),
        ("MOT9A87", "Honda", "CB 500F", 2021, "motorcycle", 95.0),
        ("TRK4B56", "Ford", "Ranger", 2023, "pickup truck", 260.0),
        ("VAN7C45", "Mercedes-Benz", "Sprinter", 2020, "van", 320.0),
    ]
    customers = [
        ("11122233344", "Ana Costa", "(11) 90000-1000", "ana@example.com", "Rua Central, 100", "ana123"),
        ("55566677788", "Bruno Lima", "(11) 90000-2000", "bruno@example.com", "Av. Norte, 250", "bruno123"),
    ]

    for plate, brand, model, year, vehicle_type, rate in vehicles:
        try:
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
        except ValueError:
            pass

    for code, name, phone, email, address, password in customers:
        try:
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
        except ValueError:
            pass

    try:
        controller.post_rental(
            {
                "customer_code": "11122233344",
                "vehicle_plate": "ABC1D23",
                "pickup_date": "2026-05-31",
                "days": 3,
            }
        )
    except ValueError:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate the vehicle rental database.")
    parser.add_argument("--reset", action="store_true", help="Delete the current database before seeding.")
    parser.add_argument("--database", default=None, help="Custom SQLite database path.")
    args = parser.parse_args()
    seed(reset=args.reset, database_path=args.database)
    print("Database populated.")


if __name__ == "__main__":
    main()
