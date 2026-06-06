
from typing import Iterable

from matheushpmoreira.vehicle_rental_system.backend.models import Customer, Rental, Vehicle, VehicleStatus, VehicleType

from matheushpmoreira.vehicle_rental_system.frontend.choices import Choice
from matheushpmoreira.vehicle_rental_system.frontend.labels import rental_status_label, vehicle_status_label, vehicle_type_label


def money(value: float) -> str:
    return f"{value:.2f}"


def vehicle_admin_payload(
    fields: dict[str, str], vehicle_type: VehicleType, status: VehicleStatus
) -> dict[str, str]:
    return {
        "plate": fields["plate"],
        "brand": fields["brand"],
        "model": fields["model"],
        "year": fields["year"],
        "vehicle_type": vehicle_type.value,
        "daily_rate": fields["daily_rate"],
        "status": status.value,
    }


def customer_payload(fields: dict[str, str]) -> dict[str, str]:
    return dict(fields)


def rental_payload(customer_code: str, vehicle_plate: str, pickup_date: str, days: str) -> dict[str, str]:
    return {
        "customer_code": customer_code,
        "vehicle_plate": vehicle_plate,
        "pickup_date": pickup_date,
        "days": days,
    }


def vehicle_admin_row(vehicle: Vehicle) -> tuple[object, ...]:
    return (
        vehicle.plate,
        vehicle.brand,
        vehicle.model,
        vehicle.year,
        vehicle_type_label(vehicle.vehicle_type),
        money(vehicle.daily_rate),
        vehicle_status_label(vehicle.status),
    )


def customer_admin_row(customer: Customer) -> tuple[object, ...]:
    return customer.code, customer.name, customer.phone, customer.email, customer.address, customer.password


def rental_admin_row(rental: Rental) -> tuple[object, ...]:
    return (
        rental.rental_id,
        rental.customer_code,
        rental.vehicle_plate,
        rental.pickup_date.isoformat(),
        rental.expected_return_date.isoformat(),
        rental.days,
        money(rental.total_amount),
        rental_status_label(rental.status),
    )


def public_vehicle_row(vehicle: Vehicle) -> tuple[object, ...]:
    return (
        vehicle.plate,
        vehicle.brand,
        vehicle.model,
        vehicle.year,
        vehicle_type_label(vehicle.vehicle_type),
        money(vehicle.daily_rate),
    )


def public_rental_row(rental: Rental) -> tuple[object, ...]:
    return (
        rental.rental_id,
        rental.vehicle_plate,
        rental.pickup_date.isoformat(),
        rental.expected_return_date.isoformat(),
        rental.days,
        money(rental.total_amount),
        rental_status_label(rental.status),
    )


def customer_choices(customers: Iterable[Customer]) -> tuple[Choice[str], ...]:
    return tuple(Choice(customer.code, f"{customer.code} - {customer.name}") for customer in customers)


def available_vehicle_choices(vehicles: Iterable[Vehicle]) -> tuple[Choice[str], ...]:
    return tuple(
        Choice(vehicle.plate, f"{vehicle.plate} - {vehicle.brand} {vehicle.model} ({money(vehicle.daily_rate)})")
        for vehicle in vehicles
    )


def available_vehicle_filter() -> dict[str, str]:
    return {"status": VehicleStatus.AVAILABLE.value}
