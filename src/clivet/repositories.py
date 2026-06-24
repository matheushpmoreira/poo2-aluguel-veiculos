import sqlite3
from datetime import date, datetime
from typing import Iterable

from clivet.database import Database
from clivet.errors import ConflictError, NotFoundError
from clivet.models import (
    Animal,
    BathGrooming,
    Bird,
    Booking,
    BookingStatus,
    Cat,
    Consultation,
    Dog,
    Housing,
    Service,
    ServiceType,
    Species,
    Tutor,
    Vaccination,
)


class TutorRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, tutor: Tutor) -> None:
        try:
            with self.database.connect() as connection:
                connection.execute(
                    "INSERT INTO tutors (cpf, name, phone, email, address) VALUES (?, ?, ?, ?, ?)",
                    (tutor.cpf, tutor.name, tutor.phone, tutor.email, tutor.address),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Já existe um tutor com este CPF.") from exc

    def update(self, tutor: Tutor) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE tutors
                SET name = ?, phone = ?, email = ?, address = ?
                WHERE cpf = ?
                """,
                (tutor.name, tutor.phone, tutor.email, tutor.address, tutor.cpf),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Tutor não encontrado.")

    def delete(self, cpf: str) -> None:
        try:
            with self.database.connect() as connection:
                cursor = connection.execute("DELETE FROM tutors WHERE cpf = ?", (cpf.strip(),))
                if cursor.rowcount == 0:
                    raise NotFoundError("Tutor não encontrado.")
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Não é possível remover um tutor com animais cadastrados.") from exc

    def get(self, cpf: str) -> Tutor | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM tutors WHERE cpf = ?", (cpf.strip(),)).fetchone()
        return self._parse_row(row) if row else None

    def list(self) -> list[Tutor]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM tutors ORDER BY name").fetchall()
        return [self._parse_row(row) for row in rows]

    @staticmethod
    def _parse_row(row: sqlite3.Row) -> Tutor:
        return Tutor(
            cpf=row["cpf"],
            name=row["name"],
            phone=row["phone"],
            email=row["email"],
            address=row["address"],
        )


class AnimalRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, animal: Animal) -> None:
        try:
            with self.database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO animals (
                        code, name, species, breed, birthday, weight, tutor_cpf, status,
                        dog_size, rabies_vaccinated, cat_neutered, cat_hair_type,
                        bird_leg_band, bird_exotic
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._params(animal),
                )
        except sqlite3.IntegrityError as exc:
            if "FOREIGN KEY" in str(exc):
                raise NotFoundError("O animal exige um tutor cadastrado.") from exc
            raise ConflictError("Já existe um animal com este código.") from exc

    def update(self, animal: Animal) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE animals
                SET name = ?, species = ?, breed = ?, birthday = ?, weight = ?, tutor_cpf = ?, status = ?,
                    dog_size = ?, rabies_vaccinated = ?, cat_neutered = ?, cat_hair_type = ?,
                    bird_leg_band = ?, bird_exotic = ?
                WHERE code = ?
                """,
                (
                    animal.name,
                    animal.species.value,
                    animal.breed,
                    animal.birthday.isoformat(),
                    animal.weight,
                    animal.tutor_cpf,
                    animal.status.value,
                    getattr(animal, "size", None),
                    1 if getattr(animal, "rabies_vaccinated", False) else 0,
                    1 if getattr(animal, "neutered", False) else 0,
                    getattr(animal, "hair_type", None),
                    getattr(animal, "leg_band", ""),
                    1 if getattr(animal, "exotic", False) else 0,
                    animal.code,
                ),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Animal não encontrado.")

    def delete(self, code: str) -> None:
        try:
            with self.database.connect() as connection:
                cursor = connection.execute("DELETE FROM animals WHERE code = ?", (code.strip().upper(),))
                if cursor.rowcount == 0:
                    raise NotFoundError("Animal não encontrado.")
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Não é possível remover um animal com agendamentos cadastrados.") from exc

    def get(self, code: str) -> Animal | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM animals WHERE code = ?", (code.strip().upper(),)).fetchone()
        return self._parse_row(row) if row else None

    def list(self, tutor_cpf: str = "") -> list[Animal]:
        params: tuple[str, ...] = ()
        where = ""
        if tutor_cpf.strip():
            where = "WHERE tutor_cpf = ?"
            params = (tutor_cpf.strip(),)
        with self.database.connect() as connection:
            rows = connection.execute(f"SELECT * FROM animals {where} ORDER BY name", params).fetchall()
        return [self._parse_row(row) for row in rows]

    @staticmethod
    def _params(animal: Animal) -> tuple[object, ...]:
        return (
            animal.code,
            animal.name,
            animal.species.value,
            animal.breed,
            animal.birthday.isoformat(),
            animal.weight,
            animal.tutor_cpf,
            animal.status.value,
            getattr(animal, "size", None),
            1 if getattr(animal, "rabies_vaccinated", False) else 0,
            1 if getattr(animal, "neutered", False) else 0,
            getattr(animal, "hair_type", None),
            getattr(animal, "leg_band", ""),
            1 if getattr(animal, "exotic", False) else 0,
        )

    @staticmethod
    def _parse_row(row: sqlite3.Row) -> Animal:
        base = {
            "code": row["code"],
            "name": row["name"],
            "species": row["species"],
            "breed": row["breed"],
            "birthday": date.fromisoformat(row["birthday"]),
            "weight": row["weight"],
            "tutor_cpf": row["tutor_cpf"],
            "status": row["status"],
        }
        species = Species(row["species"])
        if species == Species.DOG:
            return Dog(
                **base,
                size=row["dog_size"] or "medium",
                rabies_vaccinated=bool(int(row["rabies_vaccinated"] or 0)),
            )
        if species == Species.CAT:
            return Cat(
                **base,
                neutered=bool(int(row["cat_neutered"] or 0)),
                hair_type=row["cat_hair_type"] or "short",
            )
        return Bird(
            **base,
            leg_band=row["bird_leg_band"] or "",
            exotic=bool(int(row["bird_exotic"] or 0)),
        )


class ServiceRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, service: Service) -> None:
        try:
            with self.database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO services (
                        code, name, service_type, description, base_value, duration_minutes,
                        veterinarian, specialty, nail_clipping, perfume, batch, expiration_date,
                        laboratory, daily_rate, accommodation_capacity
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._params(service),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Já existe um serviço com este código.") from exc

    def update(self, service: Service) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE services
                SET name = ?, service_type = ?, description = ?, base_value = ?, duration_minutes = ?,
                    veterinarian = ?, specialty = ?, nail_clipping = ?, perfume = ?, batch = ?,
                    expiration_date = ?, laboratory = ?, daily_rate = ?, accommodation_capacity = ?
                WHERE code = ?
                """,
                self._params(service)[1:] + (service.code,),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Serviço não encontrado.")

    def delete(self, code: str) -> None:
        try:
            with self.database.connect() as connection:
                cursor = connection.execute("DELETE FROM services WHERE code = ?", (code.strip().upper(),))
                if cursor.rowcount == 0:
                    raise NotFoundError("Serviço não encontrado.")
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Não é possível remover um serviço usado em agendamentos.") from exc

    def get(self, code: str) -> Service | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM services WHERE code = ?", (code.strip().upper(),)).fetchone()
        return self._parse_row(row) if row else None

    def get_many(self, codes: Iterable[str]) -> list[Service]:
        return [service for code in codes if (service := self.get(code)) is not None]

    def list(self) -> list[Service]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM services ORDER BY name").fetchall()
        return [self._parse_row(row) for row in rows]

    @staticmethod
    def _params(service: Service) -> tuple[object, ...]:
        return (
            service.code,
            service.name,
            service.service_type.value,
            service.description,
            service.base_value,
            service.duration_minutes,
            getattr(service, "veterinarian", ""),
            getattr(service, "specialty", ""),
            1 if getattr(service, "nail_clipping", False) else 0,
            1 if getattr(service, "perfume", False) else 0,
            getattr(service, "batch", ""),
            getattr(service, "expiration_date", None).isoformat()
            if getattr(service, "expiration_date", None)
            else None,
            getattr(service, "laboratory", ""),
            getattr(service, "daily_rate", 0.0),
            getattr(service, "accommodation_capacity", 0),
        )

    @staticmethod
    def _parse_row(row: sqlite3.Row) -> Service:
        base = {
            "code": row["code"],
            "name": row["name"],
            "service_type": row["service_type"],
            "description": row["description"],
            "base_value": row["base_value"],
            "duration_minutes": row["duration_minutes"],
        }
        service_type = ServiceType(row["service_type"])
        if service_type == ServiceType.CONSULTATION:
            return Consultation(**base, veterinarian=row["veterinarian"] or "", specialty=row["specialty"] or "")
        if service_type == ServiceType.BATH_GROOMING:
            return BathGrooming(
                **base,
                nail_clipping=bool(int(row["nail_clipping"] or 0)),
                perfume=bool(int(row["perfume"] or 0)),
            )
        if service_type == ServiceType.VACCINATION:
            expiration_date = date.fromisoformat(row["expiration_date"]) if row["expiration_date"] else None
            return Vaccination(
                **base,
                batch=row["batch"] or "",
                expiration_date=expiration_date,
                laboratory=row["laboratory"] or "",
            )
        if service_type == ServiceType.HOUSING:
            return Housing(
                **base,
                daily_rate=row["daily_rate"] or row["base_value"],
                accommodation_capacity=row["accommodation_capacity"] or 1,
            )
        return Service(**base)


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

