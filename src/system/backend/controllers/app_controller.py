from __future__ import annotations

from pathlib import Path

from system.backend.database import Database
from system.backend.repositories import CustomerRepository, RentalRepository, VehicleRepository
from system.backend.services import CustomerService, RentalService, VehicleService


class AppController:
    def __init__(self, database_path: str | Path | None = None) -> None:
        self.database = Database(database_path) if database_path else Database()
        self.vehicle_repository = VehicleRepository(self.database)
        self.customer_repository = CustomerRepository(self.database)
        self.rental_repository = RentalRepository(self.database)
        self.vehicles = VehicleService(self.vehicle_repository)
        self.customers = CustomerService(self.customer_repository)
        self.rentals = RentalService(
            rental_repository=self.rental_repository,
            customer_repository=self.customer_repository,
            vehicle_repository=self.vehicle_repository,
        )
