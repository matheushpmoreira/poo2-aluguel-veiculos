from __future__ import annotations

from datetime import date

from system.backend.database import Database
from system.backend.errors import NotFoundError, UnprocessableEntityError
from system.backend.models.rental import Rental


class RentalRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, rental: Rental) -> Rental:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO rentals
                    (customer_code, vehicle_plate, pickup_date, expected_return_date, days, total_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rental.customer_code,
                    rental.vehicle_plate,
                    rental.pickup_date.isoformat(),
                    rental.expected_return_date.isoformat(),
                    rental.days,
                    rental.total_amount,
                    rental.status.value,
                ),
            )

            rental.rental_id = cursor.lastrowid
        return rental

    def update(self, rental: Rental) -> None:
        if rental.rental_id is None:
            raise UnprocessableEntityError("Rental id is required.")

        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE rentals
                SET customer_code = ?, vehicle_plate = ?, pickup_date = ?, expected_return_date = ?,
                    days = ?, total_amount = ?, status = ?
                WHERE rental_id = ?
                """,
                (
                    rental.customer_code,
                    rental.vehicle_plate,
                    rental.pickup_date.isoformat(),
                    rental.expected_return_date.isoformat(),
                    rental.days,
                    rental.total_amount,
                    rental.status.value,
                    rental.rental_id,
                ),
            )

            if cursor.rowcount == 0:
                raise NotFoundError("Rental was not found.")

    def get_by_id(self, rental_id: int) -> Rental | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM rentals WHERE rental_id = ?", (rental_id,)).fetchone()
        return self._parse_row(row) if row else None

    def get_all(self) -> list[Rental]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM rentals ORDER BY rental_id DESC").fetchall()
        return [self._parse_row(row) for row in rows]

    def get_by_customer(self, customer_code: str) -> list[Rental]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM rentals WHERE customer_code = ? ORDER BY rental_id DESC",
                (customer_code.strip(),),
            ).fetchall()
        return [self._parse_row(row) for row in rows]

    def has_active_rental_for_vehicle(self, vehicle_plate: str) -> bool:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM rentals WHERE vehicle_plate = ? AND status = 'active' LIMIT 1",
                (vehicle_plate.strip().upper(),),
            ).fetchone()
        return row is not None

    @staticmethod
    def _parse_row(row) -> Rental:
        return Rental(
            rental_id=row["rental_id"],
            customer_code=row["customer_code"],
            vehicle_plate=row["vehicle_plate"],
            pickup_date=date.fromisoformat(row["pickup_date"]),
            expected_return_date=date.fromisoformat(row["expected_return_date"]),
            days=row["days"],
            total_amount=row["total_amount"],
            status=row["status"],
        )
