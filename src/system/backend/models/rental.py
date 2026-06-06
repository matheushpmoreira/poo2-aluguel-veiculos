from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from system.backend.errors import UnprocessableEntityError

from .customer import Customer
from .vehicle import Vehicle


class RentalStatus(StrEnum):
    ACTIVE = "active"
    FINISHED = "finished"


ACTIVE = RentalStatus.ACTIVE
FINISHED = RentalStatus.FINISHED


@dataclass
class Rental:
    customer_code: str
    vehicle_plate: str
    pickup_date: date
    expected_return_date: date
    days: int
    total_amount: float
    status: RentalStatus = ACTIVE
    rental_id: int | None = None
    customer: Customer | None = None
    vehicle: Vehicle | None = None

    def __post_init__(self) -> None:
        self.customer_code = self.customer_code.strip()
        self.vehicle_plate = self.vehicle_plate.strip().upper()
        try:
            self.status = RentalStatus(str(self.status).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("Rental status must be active or finished.") from exc

        if not self.customer_code or not self.vehicle_plate:
            raise UnprocessableEntityError("Rental customer and vehicle are required.")
        if self.days <= 0:
            raise UnprocessableEntityError("Rental days must be greater than zero.")
        if self.total_amount < 0:
            raise UnprocessableEntityError("Rental total amount cannot be negative.")
        if self.expected_return_date < self.pickup_date:
            raise UnprocessableEntityError("Expected return date cannot be before pickup date.")

    @classmethod
    def create(cls, customer: Customer, vehicle: Vehicle, pickup_date: date, days: int) -> "Rental":
        return cls(
            customer_code=customer.code,
            vehicle_plate=vehicle.plate,
            pickup_date=pickup_date,
            expected_return_date=date.fromordinal(pickup_date.toordinal() + days),
            days=days,
            total_amount=vehicle.calc_rental_cost(days),
            customer=customer,
            vehicle=vehicle,
        )

    def set_finished(self) -> None:
        self.status = FINISHED
