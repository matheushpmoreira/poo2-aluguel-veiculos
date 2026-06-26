import sqlite3
from datetime import date
from typing import Iterable

from clivet.database import Database
from clivet.errors import ConflictError, NotFoundError
from clivet.models import BathGrooming, Consultation, Housing, Service, ServiceType, Vaccination
from clivet.repositories.base import Repository


class ServiceRepository(Repository):
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
