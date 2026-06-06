
import sqlite3

from matheushpmoreira.vehicle_rental_system.backend.errors import ConflictError, NotFoundError, UnprocessableEntityError
from matheushpmoreira.vehicle_rental_system.backend.models.vehicle import Vehicle, VehicleStatus, VehicleType
from matheushpmoreira.vehicle_rental_system.backend.repositories.vehicle_repository import VehicleRepository


class VehicleService:
    def __init__(self, vehicle_repository: VehicleRepository) -> None:
        self.vehicle_repository = vehicle_repository

    def create_vehicle(
        self,
        plate: str,
        brand: str,
        model: str,
        year: int,
        vehicle_type: VehicleType,
        daily_rate: float,
        status: VehicleStatus = VehicleStatus.AVAILABLE,
    ) -> Vehicle:
        vehicle = Vehicle(plate, brand, model, year, vehicle_type, daily_rate, status)

        try:
            self.vehicle_repository.insert(vehicle)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Já existe um veículo com esta placa.") from exc
        return vehicle

    def update_vehicle(
        self,
        plate: str,
        brand: str,
        model: str,
        year: int,
        vehicle_type: VehicleType,
        daily_rate: float,
        status: VehicleStatus,
    ) -> Vehicle:
        if status not in VehicleStatus:
            raise UnprocessableEntityError("O status do veículo deve ser disponível ou alugado.")

        vehicle = Vehicle(plate, brand, model, year, vehicle_type, daily_rate, status)
        self.vehicle_repository.update(vehicle)
        return vehicle

    def delete_vehicle(self, plate: str) -> None:
        vehicle = self.get_vehicle(plate)

        if vehicle.status == VehicleStatus.RENTED:
            raise ConflictError("Um veículo alugado não pode ser removido.")
        try:
            self.vehicle_repository.delete(plate)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("O veículo possui histórico de aluguel e não pode ser removido.") from exc

    def get_vehicle(self, plate: str) -> Vehicle:
        vehicle = self.vehicle_repository.get_by_plate(plate)

        if vehicle is None:
            raise NotFoundError("Veículo não encontrado.")

        return vehicle

    def list_vehicles(self) -> list[Vehicle]:
        return self.vehicle_repository.get_all()

    def search_vehicles(self, **kwargs: str) -> list[Vehicle]:
        # return self.vehicle_repository.search(text, status)
        return self.vehicle_repository.search(
            **{k: v for k, v in kwargs.items() if k in ("brand", "model", "plate", "status")}
        )
