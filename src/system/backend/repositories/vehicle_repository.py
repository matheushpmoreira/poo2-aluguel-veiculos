
from system.backend.database import Database
from system.backend.errors import NotFoundError
from system.backend.models.vehicle import Vehicle


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
                    vehicle.vehicle_type.value,
                    vehicle.daily_rate,
                    vehicle.status.value,
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
                    vehicle.vehicle_type.value,
                    vehicle.daily_rate,
                    vehicle.status.value,
                    vehicle.plate,
                ),
            )

            if cursor.rowcount == 0:
                raise NotFoundError("Veículo não encontrado.")

    def delete(self, plate: str) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM vehicles WHERE plate = ?", (plate.strip().upper(),))
            if cursor.rowcount == 0:
                raise NotFoundError("Veículo não encontrado.")

    def get_by_plate(self, plate: str) -> Vehicle | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM vehicles WHERE plate = ?", (plate.strip().upper(),)).fetchone()
        return self._parse_row(row) if row else None

    def get_all(self) -> list[Vehicle]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM vehicles ORDER BY plate").fetchall()
        return [self._parse_row(row) for row in rows]

    def search(self, *, brand: str = "", model: str = "", plate: str = "", status: str = "") -> list[Vehicle]:
        query = """
            SELECT * FROM vehicles
            WHERE (? = '' OR lower(brand) LIKE ?)
              AND (? = '' OR lower(model) LIKE ?)
              AND (? = '' OR lower(plate) LIKE ?)
              AND (? = '' OR status = ?)
            ORDER BY plate
        """

        normalized_brand = brand.strip().lower()
        normalized_model = model.strip().lower()
        normalized_plate = plate.strip().lower()
        normalized_status = status.strip().lower()
        parameters = (
            normalized_brand,
            f"%{normalized_brand}%",
            normalized_model,
            f"%{normalized_model}%",
            normalized_plate,
            f"%{normalized_plate}%",
            normalized_status,
            normalized_status,
        )

        with self.database.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._parse_row(row) for row in rows]

    @staticmethod
    def _parse_row(row) -> Vehicle:
        return Vehicle(
            plate=row["plate"],
            brand=row["brand"],
            model=row["model"],
            year=row["year"],
            vehicle_type=row["vehicle_type"],
            daily_rate=row["daily_rate"],
            status=row["status"],
        )
