from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .customer import Customer
from .vehicle import Vehicle


ACTIVE = "active"
FINISHED = "finished"


@dataclass
class Rental:
    customer_code: str
    vehicle_plate: str
    pickup_date: date
    expected_return_date: date
    days: int
    total_amount: float
    status: str = ACTIVE
    rental_id: int | None = None
    customer: Customer | None = None
    vehicle: Vehicle | None = None

    def __post_init__(self) -> None:
        self.customer_code = self.customer_code.strip()
        self.vehicle_plate = self.vehicle_plate.strip().upper()
        self.status = self.status.strip().lower()
        if not self.customer_code or not self.vehicle_plate:
            raise ValueError("Rental customer and vehicle are required.")
        if self.days <= 0:
            raise ValueError("Rental days must be greater than zero.")
        if self.total_amount < 0:
            raise ValueError("Rental total amount cannot be negative.")
        if self.expected_return_date < self.pickup_date:
            raise ValueError("Expected return date cannot be before pickup date.")
        if self.status not in {ACTIVE, FINISHED}:
            raise ValueError("Rental status must be active or finished.")

    @classmethod
    def create(cls, customer: Customer, vehicle: Vehicle, pickup_date: date, days: int) -> "Rental":
        total_amount = vehicle.rental_cost(days)
        return cls(
            customer_code=customer.code,
            vehicle_plate=vehicle.plate,
            pickup_date=pickup_date,
            expected_return_date=date.fromordinal(pickup_date.toordinal() + days),
            days=days,
            total_amount=total_amount,
            customer=customer,
            vehicle=vehicle,
        )

    def finish(self) -> None:
        self.status = FINISHED
