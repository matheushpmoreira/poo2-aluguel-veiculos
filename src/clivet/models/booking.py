from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum

from clivet.errors import UnprocessableEntityError
from clivet.models.animal import Animal
from clivet.models.service import Service


class BookingStatus(StrEnum):
    BOOKED = "booked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"
    MISSED = "missed"


@dataclass
class Booking:
    code: str
    animal_code: str
    service_codes: list[str]
    start_at: datetime
    end_at: datetime
    total_value: float
    status: BookingStatus = BookingStatus.BOOKED
    observations: str = ""
    animal: Animal | None = None
    services: list[Service] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.code = self.code.strip().upper()
        self.animal_code = self.animal_code.strip().upper()
        self.service_codes = [code.strip().upper() for code in self.service_codes if code.strip()]
        self.observations = self.observations.strip()
        try:
            self.status = BookingStatus(str(self.status).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("O status do agendamento é inválido.") from exc

        if not self.code or not self.animal_code or not self.service_codes:
            raise UnprocessableEntityError("Código, animal e serviços são obrigatórios para o agendamento.")
        if self.end_at <= self.start_at:
            raise UnprocessableEntityError("O término estimado deve ser posterior ao início.")
        if self.total_value < 0:
            raise UnprocessableEntityError("O valor total do agendamento não pode ser negativo.")

    @classmethod
    def create(
        cls,
        code: str,
        animal: Animal,
        services: list[Service],
        start_at: datetime,
        observations: str = "",
        status: BookingStatus = BookingStatus.BOOKED,
    ) -> "Booking":
        if not services:
            raise UnprocessableEntityError("Selecione pelo menos um serviço.")
        duration = sum(service.duration_minutes for service in services)
        base_total = sum(service.base_value for service in services)
        multiplier = 1.2 if start_at.weekday() >= 5 else 1.0
        return cls(
            code=code,
            animal_code=animal.code,
            service_codes=[service.code for service in services],
            start_at=start_at,
            end_at=start_at + timedelta(minutes=duration),
            total_value=round(base_total * multiplier, 2),
            status=status,
            observations=observations,
            animal=animal,
            services=services,
        )

    def overlaps(self, other: "Booking") -> bool:
        return self.start_at < other.end_at and self.end_at > other.start_at
