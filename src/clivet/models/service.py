from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from clivet.errors import UnprocessableEntityError


class ServiceType(StrEnum):
    CONSULTATION = "consultation"
    BATH_GROOMING = "bath_grooming"
    VACCINATION = "vaccination"
    EXAM = "exam"
    SURGERY = "surgery"
    HOUSING = "housing"


@dataclass
class Service:
    code: str
    name: str
    service_type: ServiceType
    description: str
    base_value: float
    duration_minutes: int

    def __post_init__(self) -> None:
        self.code = self.code.strip().upper()
        self.name = self.name.strip()
        self.description = self.description.strip()
        try:
            self.service_type = ServiceType(str(self.service_type).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("O tipo de serviço é inválido.") from exc

        if not self.code or not self.name or not self.description:
            raise UnprocessableEntityError("Código, nome e descrição do serviço são obrigatórios.")
        if self.base_value <= 0:
            raise UnprocessableEntityError("O valor base do serviço deve ser maior que zero.")
        if self.duration_minutes <= 0:
            raise UnprocessableEntityError("A duração estimada deve ser maior que zero.")


@dataclass
class Consultation(Service):
    veterinarian: str = ""
    specialty: str = ""

    def __post_init__(self) -> None:
        self.service_type = ServiceType.CONSULTATION
        super().__post_init__()
        self.veterinarian = self.veterinarian.strip()
        self.specialty = self.specialty.strip()
        if not self.veterinarian:
            raise UnprocessableEntityError("O veterinário da consulta é obrigatório.")


@dataclass
class BathGrooming(Service):
    nail_clipping: bool = False
    perfume: bool = False

    def __post_init__(self) -> None:
        self.service_type = ServiceType.BATH_GROOMING
        super().__post_init__()


@dataclass
class Vaccination(Service):
    batch: str = ""
    expiration_date: date | None = None
    laboratory: str = ""

    def __post_init__(self) -> None:
        self.service_type = ServiceType.VACCINATION
        super().__post_init__()
        self.batch = self.batch.strip()
        self.laboratory = self.laboratory.strip()
        if not self.batch or not self.expiration_date or not self.laboratory:
            raise UnprocessableEntityError("Lote, validade e laboratório da vacina são obrigatórios.")


@dataclass
class Housing(Service):
    daily_rate: float = 0.0
    accommodation_capacity: int = 1

    def __post_init__(self) -> None:
        self.service_type = ServiceType.HOUSING
        super().__post_init__()
        if self.daily_rate <= 0:
            raise UnprocessableEntityError("A diária da hospedagem deve ser maior que zero.")
        if self.accommodation_capacity <= 0:
            raise UnprocessableEntityError("A capacidade da hospedagem deve ser maior que zero.")
