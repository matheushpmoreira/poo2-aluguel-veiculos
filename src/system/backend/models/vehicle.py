from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from system.backend.errors import ConflictError, UnprocessableEntityError


class VehicleStatus(StrEnum):
    AVAILABLE = "available"
    RENTED = "rented"


class VehicleType(StrEnum):
    CAR = "car"
    VAN = "van"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"


@dataclass
class Vehicle:
    plate: str
    brand: str
    model: str
    year: int
    vehicle_type: VehicleType
    daily_rate: float
    status: VehicleStatus = VehicleStatus.AVAILABLE

    def __post_init__(self) -> None:
        self.plate = self.plate.strip().upper()
        self.brand = self.brand.strip()
        self.model = self.model.strip()
        try:
            self.status = VehicleStatus(str(self.status).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("O status do veículo deve ser disponível ou alugado.") from exc
        try:
            self.vehicle_type = VehicleType(str(self.vehicle_type).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("O tipo do veículo deve ser carro, moto, caminhão ou van.") from exc

        if not self.plate or not self.brand or not self.model:
            raise UnprocessableEntityError("Placa, marca e modelo do veículo são obrigatórios.")
        if not (0 < self.year < date.today().year):
            raise UnprocessableEntityError("O ano do veículo é inválido.")
        if self.daily_rate <= 0:
            raise UnprocessableEntityError("O valor da diária deve ser maior que zero.")

    @property
    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def set_rented(self) -> None:
        if not self.is_available:
            raise ConflictError("O veículo já está alugado.")
        self.status = VehicleStatus.RENTED

    def set_available(self) -> None:
        self.status = VehicleStatus.AVAILABLE

    def calc_rental_cost(self, days: int) -> float:
        if days <= 0:
            raise UnprocessableEntityError("A quantidade de dias deve ser maior que zero.")
        return round(self.daily_rate * days, 2)
