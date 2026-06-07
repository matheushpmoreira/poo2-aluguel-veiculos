
from dataclasses import dataclass
from matheushpmoreira.vehicle_rental_system.backend.models import VehicleStatus, VehicleType
from matheushpmoreira.vehicle_rental_system.frontend.labels import vehicle_status_label, vehicle_type_label


@dataclass(frozen=True)
class Option:
    value: str
    label: str


def vehicle_type_choices() -> tuple[Option, ...]:
    return tuple(Option(vehicle_type.value, vehicle_type_label(vehicle_type)) for vehicle_type in VehicleType)


def vehicle_status_choices() -> tuple[Option, ...]:
    return tuple(Option(status.value, vehicle_status_label(status)) for status in VehicleStatus)


def vehicle_status_filter_choices() -> tuple[Option, ...]:
    return Option("", ""), *vehicle_status_choices()
