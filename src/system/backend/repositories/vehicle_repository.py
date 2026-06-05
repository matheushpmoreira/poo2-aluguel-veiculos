from __future__ import annotations

from itertools import chain, repeat

from system.backend.database import Database
from system.backend.models.vehicle import Vehicle, create_vehicle


class VehicleRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, vehicle: Vehicle) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO vehicles (plate, brand, model, year, vehicle_type, daily_rate, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    vehicle.plate,
                    vehicle.brand,
                    vehicle.model,
                    vehicle.year,
                    vehicle.vehicle_type,
                    vehicle.daily_rate,
                    vehicle.status,
                ),
            )

    def update(self, vehicle: Vehicle) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE vehicles
                SET brand = ?, model = ?, year = ?, vehicle_type = ?, daily_rate = ?, status = ?
                WHERE plate = ?
                """,
                (
                    vehicle.brand,
                    vehicle.model,
                    vehicle.year,
                    vehicle.vehicle_type,
                    vehicle.daily_rate,
                    vehicle.status,
                    vehicle.plate,
                ),
            )

            if cursor.rowcount == 0:
                raise ValueError("Vehicle was not found.")

    def delete(self, plate: str) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM vehicles WHERE plate = ?", (plate.strip().upper(),))
            if cursor.rowcount == 0:
                raise ValueError("Vehicle was not found.")

    def get_by_plate(self, plate: str) -> Vehicle | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM vehicles WHERE plate = ?", (plate.strip().upper(),)).fetchone()
        return self._parse_row(row) if row else None

    def get_all(self) -> list[Vehicle]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM vehicles ORDER BY plate").fetchall()
        return [self._parse_row(row) for row in rows]

    # DO NOT DELETE: confirm refactor is working
    # def search(self, text: str = "", status: str = "") -> list[Vehicle]:
    def search(self, brand: str = "", model: str = "", plate: str = "", status: str = "") -> list[Vehicle]:
        query = """
            SELECT * FROM vehicles
            WHERE (? = '' OR brand LIKE ? OR model LIKE ? OR plate LIKE ?) AND (? = '' OR status = ?)
            ORDER BY plate
        """

        parameters = (brand, brand, model, model, plate, plate, status, status)

        with self.database.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._parse_row(row) for row in rows]

        # DO NOT DELETE: confirm refactor is working
        # normalized_text = text.strip().lower()
        # pattern = f"%{normalized_text}%"
        # normalized_status = status.strip().lower()
        # with self.database.connect() as connection:
        #     rows = connection.execute(
        #         query,
        #         (normalized_text, pattern, pattern, pattern, normalized_status, normalized_status),
        #     ).fetchall()
        # return [self._parse_row(row) for row in rows]

    @staticmethod
    def _parse_row(row) -> Vehicle:
        return create_vehicle(
            plate=row["plate"],
            brand=row["brand"],
            model=row["model"],
            year=row["year"],
            vehicle_type=row["vehicle_type"],
            daily_rate=row["daily_rate"],
            status=row["status"],
        )
