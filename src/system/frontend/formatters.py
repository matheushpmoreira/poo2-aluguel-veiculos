from __future__ import annotations

from typing import Iterable

from system.backend.models import Customer, Rental, RentalStatus, Vehicle, VehicleStatus, VehicleType

from .choices import Choice
from .labels import rental_status_label, vehicle_status_label, vehicle_type_label


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


def customer_row(customer: Customer) -> tuple[object, ...]:
    return (customer.code, customer.name, customer.phone, customer.email, customer.address, customer.password)


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


def report_vehicle_row(vehicle: Vehicle) -> tuple[object, ...]:
    return (vehicle.plate, vehicle.brand, vehicle.model, vehicle_type_label(vehicle.vehicle_type), money(vehicle.daily_rate))


def report_rental_row(item: tuple[Rental, float]) -> tuple[object, ...]:
    rental, late_fee = item
    return (
        rental.rental_id,
        rental.customer_code,
        rental.vehicle_plate,
        rental.expected_return_date.isoformat(),
        money(rental.total_amount),
        money(late_fee),
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


def active_rental_filter() -> dict[str, str]:
    return {"status": RentalStatus.ACTIVE.value}


def report_csv_rows(vehicles: Iterable[Vehicle], rentals_with_fees: Iterable[tuple[Rental, float]]) -> list[list[object]]:
    rows: list[list[object]] = [
        ["Veículos disponíveis"],
        ["placa", "marca", "modelo", "tipo", "valor_diaria"],
    ]
    for vehicle in vehicles:
        rows.append(list(report_vehicle_row(vehicle)))
    rows.extend(
        [
            [],
            ["Aluguéis ativos"],
            ["id", "cliente", "veiculo", "devolucao_prevista", "total", "multa"],
        ]
    )
    for rental_with_fee in rentals_with_fees:
        rows.append(list(report_rental_row(rental_with_fee)))
    return rows
