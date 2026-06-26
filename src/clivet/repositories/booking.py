import sqlite3
from datetime import date, datetime

from clivet.database import Database
from clivet.errors import ConflictError, NotFoundError
from clivet.models import Booking, BookingStatus, Service
from clivet.repositories.animal import AnimalRepository
from clivet.repositories.service import ServiceRepository


class BookingRepository:
    def __init__(
        self, database: Database, animal_repository: AnimalRepository, service_repository: ServiceRepository
    ) -> None:
        self.database = database
        self.animal_repository = animal_repository
        self.service_repository = service_repository

    def insert(self, booking: Booking) -> None:
        try:
            with self.database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO bookings (code, animal_code, start_at, end_at, total_value, status, observations)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        booking.code,
                        booking.animal_code,
                        booking.start_at.isoformat(timespec="minutes"),
                        booking.end_at.isoformat(timespec="minutes"),
                        booking.total_value,
                        booking.status.value,
                        booking.observations,
                    ),
                )
                self._insert_services(connection, booking)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Já existe um agendamento com este código.") from exc

    def update(self, booking: Booking) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE bookings
                SET animal_code = ?, start_at = ?, end_at = ?, total_value = ?, status = ?, observations = ?
                WHERE code = ?
                """,
                (
                    booking.animal_code,
                    booking.start_at.isoformat(timespec="minutes"),
                    booking.end_at.isoformat(timespec="minutes"),
                    booking.total_value,
                    booking.status.value,
                    booking.observations,
                    booking.code,
                ),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Agendamento não encontrado.")
            connection.execute("DELETE FROM booking_services WHERE booking_code = ?", (booking.code,))
            self._insert_services(connection, booking)

    def update_status(self, code: str, status: BookingStatus) -> Booking:
        booking = self.get(code)
        if booking is None:
            raise NotFoundError("Agendamento não encontrado.")
        booking.status = status
        self.update(booking)
        return booking

    def delete(self, code: str) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM bookings WHERE code = ?", (code.strip().upper(),))
            if cursor.rowcount == 0:
                raise NotFoundError("Agendamento não encontrado.")

    def get(self, code: str) -> Booking | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM bookings WHERE code = ?", (code.strip().upper(),)).fetchone()
        return self._parse_row(row) if row else None

    def list(
        self, animal_code: str = "", status: BookingStatus | None = None, day: date | None = None
    ) -> list[Booking]:
        clauses: list[str] = []
        params: list[object] = []
        if animal_code.strip():
            clauses.append("animal_code = ?")
            params.append(animal_code.strip().upper())
        if status is not None:
            clauses.append("status = ?")
            params.append(status.value)
        if day is not None:
            clauses.append("date(start_at) = ?")
            params.append(day.isoformat())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.database.connect() as connection:
            rows = connection.execute(f"SELECT * FROM bookings {where} ORDER BY start_at DESC", params).fetchall()
        return [self._parse_row(row) for row in rows]

    def list_overlapping(self, start_at: datetime, end_at: datetime, ignore_code: str = "") -> list[Booking]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM bookings
                WHERE start_at < ? AND end_at > ? AND status NOT IN ('canceled', 'missed') AND code != ?
                ORDER BY start_at
                """,
                (
                    end_at.isoformat(timespec="minutes"),
                    start_at.isoformat(timespec="minutes"),
                    ignore_code.strip().upper(),
                ),
            ).fetchall()
        return [self._parse_row(row) for row in rows]

    def _parse_row(self, row: sqlite3.Row) -> Booking:
        services = self._services_for(row["code"])
        animal = self.animal_repository.get(row["animal_code"])
        return Booking(
            code=row["code"],
            animal_code=row["animal_code"],
            service_codes=[service.code for service in services],
            start_at=datetime.fromisoformat(row["start_at"]),
            end_at=datetime.fromisoformat(row["end_at"]),
            total_value=row["total_value"],
            status=row["status"],
            observations=row["observations"],
            animal=animal,
            services=services,
        )

    def _services_for(self, booking_code: str) -> list[Service]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT service_code FROM booking_services
                WHERE booking_code = ?
                ORDER BY service_order
                """,
                (booking_code,),
            ).fetchall()
        return self.service_repository.get_many(row["service_code"] for row in rows)

    @staticmethod
    def _insert_services(connection: sqlite3.Connection, booking: Booking) -> None:
        connection.executemany(
            """
            INSERT INTO booking_services (booking_code, service_code, service_order)
            VALUES (?, ?, ?)
            """,
            [(booking.code, service_code, index) for index, service_code in enumerate(booking.service_codes)],
        )
