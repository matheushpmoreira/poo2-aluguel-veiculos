from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


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
            raise ValueError("Vehicle status must be available or rented.") from exc
        try:
            self.vehicle_type = VehicleType(str(self.vehicle_type).strip().lower())
        except ValueError as exc:
            raise ValueError("Vehicle type must be car, motorcycle, pickup truck or van.") from exc

        if not self.plate or not self.brand or not self.model:
            raise ValueError("Vehicle plate, brand and model are required.")
        if not (0 < self.year < date.today().year):
            raise ValueError("Vehicle year is invalid.")
        if self.daily_rate <= 0:
            raise ValueError("Vehicle daily rate must be greater than zero.")

    @property
    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def set_rented(self) -> None:
        if not self.is_available:
            raise ValueError("Vehicle is already rented.")
        self.status = VehicleStatus.RENTED

    def set_available(self) -> None:
        self.status = VehicleStatus.AVAILABLE

    def calc_rental_cost(self, days: int) -> float:
        if days <= 0:
            raise ValueError("Rental days must be greater than zero.")
        return round(self.daily_rate * days, 2)
