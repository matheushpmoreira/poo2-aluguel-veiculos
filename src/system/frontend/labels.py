from __future__ import annotations

from system.backend.models import RentalStatus, VehicleStatus, VehicleType


VEHICLE_TYPE_LABELS = {
    VehicleType.CAR: "carro",
    VehicleType.MOTORCYCLE: "moto",
    VehicleType.TRUCK: "caminhão",
    VehicleType.VAN: "van",
}
VEHICLE_STATUS_LABELS = {
    VehicleStatus.AVAILABLE: "disponível",
    VehicleStatus.RENTED: "alugado",
}
RENTAL_STATUS_LABELS = {
    RentalStatus.ACTIVE: "ativo",
    RentalStatus.FINISHED: "finalizado",
}


def vehicle_type_label(value: VehicleType | str) -> str:
    try:
        vehicle_type = VehicleType(str(value).strip().lower())
    except ValueError:
        return str(value)
    return VEHICLE_TYPE_LABELS[vehicle_type]


def vehicle_status_label(value: VehicleStatus | str) -> str:
    try:
        status = VehicleStatus(str(value).strip().lower())
    except ValueError:
        return str(value)
    return VEHICLE_STATUS_LABELS[status]


def rental_status_label(value: RentalStatus | str) -> str:
    try:
        status = RentalStatus(str(value).strip().lower())
    except ValueError:
        return str(value)
    return RENTAL_STATUS_LABELS[status]
