from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from system.backend.database import Database
from system.backend.models import Customer, Rental, Vehicle
from system.backend.repositories import CustomerRepository, RentalRepository, VehicleRepository
from system.backend.services import CustomerService, RentalService, VehicleService


class AppController:
    def __init__(self, database_path: str | Path | None = None) -> None:
        self.database = Database(database_path) if database_path else Database()
        self.vehicle_repository = VehicleRepository(self.database)
        self.customer_repository = CustomerRepository(self.database)
        self.rental_repository = RentalRepository(self.database)
        self._vehicle_service = VehicleService(self.vehicle_repository)
        self._customer_service = CustomerService(self.customer_repository)
        self._rental_service = RentalService(
            rental_repository=self.rental_repository,
            customer_repository=self.customer_repository,
            vehicle_repository=self.vehicle_repository,
        )

    def get_vehicles(self, query: dict[str, str] | None = None) -> list[Vehicle]:
        query = query or {}
        # text = str(query.get("q", "")).strip()
        # status = str(query.get("status", "")).strip()
        valid_keys = {"brand", "model", "plate", "status"}
        
        for key in query:
            if key not in valid_keys:
                del query[key]

        return self._vehicle_service.search_vehicles(**query)

        # if text:
        #     vehicles_by_plate = self._vehicle_service.search_vehicles(plate=text, status=status)
        #     vehicles_by_brand = self._vehicle_service.search_vehicles(brand=text, status=status)
        #     vehicles_by_model = self._vehicle_service.search_vehicles(model=text, status=status)
        #     vehicles = {}
        #     for vehicle in vehicles_by_plate + vehicles_by_brand + vehicles_by_model:
        #         vehicles[vehicle.plate] = vehicle
        #     return sorted(vehicles.values(), key=lambda vehicle: vehicle.plate)
        # if query:
        #     return self._vehicle_service.search_vehicles(
        #         brand=str(query.get("brand", "")),
        #         model=str(query.get("model", "")),
        #         plate=str(query.get("plate", "")),
        #         status=status,
        #     )
        # return self._vehicle_service.list_vehicles()

    def get_vehicle(self, plate: str) -> Vehicle:
        return self._vehicle_service.get_vehicle(plate)

    def post_vehicle(self, data: dict[str, Any]) -> Vehicle:
        return self._vehicle_service.create_vehicle(
            plate=str(data.get("plate", "")),
            brand=str(data.get("brand", "")),
            model=str(data.get("model", "")),
            year=self._parse_int(data.get("year"), "year"),
            vehicle_type=str(data.get("vehicle_type", "")),
            daily_rate=self._parse_float(data.get("daily_rate"), "daily rate"),
            status=str(data.get("status", "available")),
        )

    def put_vehicle(self, plate: str, data: dict[str, Any]) -> Vehicle:
        return self._vehicle_service.update_vehicle(
            plate=plate,
            brand=str(data.get("brand", "")),
            model=str(data.get("model", "")),
            year=self._parse_int(data.get("year"), "year"),
            vehicle_type=str(data.get("vehicle_type", "")),
            daily_rate=self._parse_float(data.get("daily_rate"), "daily rate"),
            status=str(data.get("status", "")),
        )

    def delete_vehicle(self, plate: str) -> None:
        self._vehicle_service.delete_vehicle(plate)

    def get_customers(self) -> list[Customer]:
        return self._customer_service.list_customers()

    def get_customer(self, code: str) -> Customer:
        return self._customer_service.get_customer(code)

    def post_customer(self, data: dict[str, Any]) -> Customer:
        return self._customer_service.create_customer(
            code=str(data.get("code", "")),
            name=str(data.get("name", "")),
            phone=str(data.get("phone", "")),
            email=str(data.get("email", "")),
            address=str(data.get("address", "")),
            password=str(data.get("password", "")),
        )

    def put_customer(self, code: str, data: dict[str, Any]) -> Customer:
        return self._customer_service.update_customer(
            code=code,
            name=str(data.get("name", "")),
            phone=str(data.get("phone", "")),
            email=str(data.get("email", "")),
            address=str(data.get("address", "")),
            password=str(data.get("password", "")),
        )

    def delete_customer(self, code: str) -> None:
        self._customer_service.delete_customer(code)

    def post_customer_login(self, data: dict[str, Any]) -> Customer:
        return self._customer_service.login(
            code=str(data.get("code", "")),
            password=str(data.get("password", "")),
        )

    def get_rentals(self, query: dict[str, Any] | None = None) -> list[Rental]:
        query = query or {}
        customer_code = str(query.get("customer_code", "")).strip()
        status = str(query.get("status", "")).strip().lower()
        if customer_code:
            rentals = self._rental_service.list_customer_rentals(customer_code)
        else:
            rentals = self._rental_service.list_rentals()
        if status:
            rentals = [rental for rental in rentals if rental.status == status]
        return rentals

    def get_rental(self, rental_id: str | int) -> Rental:
        return self._rental_service.get_rental(self._parse_int(rental_id, "rental id"))

    def post_rental(self, data: dict[str, Any]) -> Rental:
        return self._rental_service.create_rental(
            customer_code=str(data.get("customer_code", "")),
            vehicle_plate=str(data.get("vehicle_plate", "")),
            pickup_date=self._parse_date(data.get("pickup_date"), "pickup date"),
            days=self._parse_int(data.get("days"), "days"),
        )

    def post_rental_finish(self, rental_id: str | int) -> Rental:
        return self._rental_service.finish_rental(self._parse_int(rental_id, "rental id"))

    def get_rental_late_fee(self, rental_id: str | int, reference_date: date | str | None = None) -> float:
        parsed_reference_date = (
            self._parse_date(reference_date, "reference date") if reference_date is not None else None
        )
        return self._rental_service.calc_late_fee(
            rental_id=self._parse_int(rental_id, "rental id"),
            reference_date=parsed_reference_date,
        )

    @staticmethod
    def _parse_int(value: Any, field_name: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {field_name}.") from exc

    @staticmethod
    def _parse_float(value: Any, field_name: str) -> float:
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {field_name}.") from exc

    @staticmethod
    def _parse_date(value: Any, field_name: str) -> date:
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {field_name}. Use YYYY-MM-DD.") from exc
