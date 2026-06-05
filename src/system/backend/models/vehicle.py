from __future__ import annotations

from dataclasses import dataclass
from datetime import date

AVAILABLE = "available"
RENTED = "rented"


@dataclass
class Vehicle:
    plate: str
    brand: str
    model: str
    year: int
    daily_rate: float
    status: str = AVAILABLE
    vehicle_type: str = "vehicle"

    def __post_init__(self) -> None:
        self.plate = self.plate.strip().upper()
        self.brand = self.brand.strip()
        self.model = self.model.strip()
        self.status = self.status.strip().lower()
        self.vehicle_type = self.vehicle_type.strip().lower()

        if not self.plate or not self.brand or not self.model:
            raise ValueError("Vehicle plate, brand and model are required.")
        if not (0 < self.year < date.today().year):
            raise ValueError("Vehicle year is invalid.")
        if self.daily_rate <= 0:
            raise ValueError("Vehicle daily rate must be greater than zero.")
        if self.status not in {AVAILABLE, RENTED}:
            raise ValueError("Vehicle status must be available or rented.")

    @property
    def is_available(self) -> bool:
        return self.status == AVAILABLE

    def set_rented(self) -> None:
        if not self.is_available:
            raise ValueError("Vehicle is already rented.")
        self.status = RENTED

    def set_available(self) -> None:
        self.status = AVAILABLE

    def calc_rental_cost(self, days: int) -> float:
        if days <= 0:
            raise ValueError("Rental days must be greater than zero.")
        return round(self.daily_rate * days, 2)


class Car(Vehicle):
    def __init__(
        self, plate: str, brand: str, model: str, year: int, daily_rate: float, status: str = AVAILABLE
    ) -> None:
        super().__init__(plate, brand, model, year, daily_rate, status, "car")


class Motorcycle(Vehicle):
    def __init__(
        self, plate: str, brand: str, model: str, year: int, daily_rate: float, status: str = AVAILABLE
    ) -> None:
        super().__init__(plate, brand, model, year, daily_rate, status, "motorcycle")


class PickupTruck(Vehicle):
    def __init__(
        self, plate: str, brand: str, model: str, year: int, daily_rate: float, status: str = AVAILABLE
    ) -> None:
        super().__init__(plate, brand, model, year, daily_rate, status, "pickup truck")


class Van(Vehicle):
    def __init__(
        self, plate: str, brand: str, model: str, year: int, daily_rate: float, status: str = AVAILABLE
    ) -> None:
        super().__init__(plate, brand, model, year, daily_rate, status, "van")


def create_vehicle(
    plate: str,
    brand: str,
    model: str,
    year: int,
    vehicle_type: str,
    daily_rate: float,
    status: str = AVAILABLE,
) -> Vehicle:
    normalized_type = vehicle_type.strip().lower()
    vehicle_classes = {
        "car": Car,
        "motorcycle": Motorcycle,
        "pickup truck": PickupTruck,
        "van": Van,
    }
    vehicle_class = vehicle_classes.get(normalized_type)
    if vehicle_class is None:
        return Vehicle(plate, brand, model, year, daily_rate, status, normalized_type or "vehicle")
    return vehicle_class(plate, brand, model, year, daily_rate, status)
