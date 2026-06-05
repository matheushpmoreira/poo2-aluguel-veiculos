from __future__ import annotations

import sqlite3

from system.backend.models.vehicle import AVAILABLE, RENTED, Vehicle, create_vehicle
from system.backend.repositories.vehicle_repository import VehicleRepository


class VehicleService:
    def __init__(self, vehicle_repository: VehicleRepository) -> None:
        self.vehicle_repository = vehicle_repository

    def create_vehicle(
        self,
        plate: str,
        brand: str,
        model: str,
        year: int | str,
        vehicle_type: str,
        daily_rate: float | str,
        status: str = AVAILABLE,
    ) -> Vehicle:
        vehicle = create_vehicle(plate, brand, model, int(year), vehicle_type, float(daily_rate), status)

        try:
            self.vehicle_repository.insert(vehicle)
        except sqlite3.IntegrityError as exc:
            raise ValueError("A vehicle with this plate already exists.") from exc
        return vehicle

    def update_vehicle(
        self,
        plate: str,
        brand: str,
        model: str,
        year: int | str,
        vehicle_type: str,
        daily_rate: float | str,
        status: str,
    ) -> Vehicle:
        if status not in {AVAILABLE, RENTED}:
            raise ValueError("Vehicle status must be available or rented.")

        vehicle = create_vehicle(plate, brand, model, int(year), vehicle_type, float(daily_rate), status)
        self.vehicle_repository.update(vehicle)
        return vehicle

    def delete_vehicle(self, plate: str) -> None:
        vehicle = self.get_vehicle(plate)

        if vehicle.status == RENTED:
            raise ValueError("A rented vehicle cannot be deleted.")
        try:
            self.vehicle_repository.delete(plate)
        except sqlite3.IntegrityError as exc:
            raise ValueError("Vehicle has rental history and cannot be deleted.") from exc

    def get_vehicle(self, plate: str) -> Vehicle:
        vehicle = self.vehicle_repository.get_by_plate(plate)

        if vehicle is None:
            raise ValueError("Vehicle was not found.")

        return vehicle

    def list_vehicles(self) -> list[Vehicle]:
        return self.vehicle_repository.get_all()

    def search_vehicles(self, **kwargs: dict[str, str]) -> list[Vehicle]:
        # return self.vehicle_repository.search(text, status)
        return self.vehicle_repository.search(
            **{k: v for k, v in kwargs.items() if k in ("brand", "model", "plate", "status")}
        )
