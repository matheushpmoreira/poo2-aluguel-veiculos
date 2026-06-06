
from datetime import date

from system.backend.errors import ConflictError, NotFoundError
from system.backend.models.rental import ACTIVE, Rental
from system.backend.repositories import CustomerRepository, RentalRepository, VehicleRepository


class RentalService:
    def __init__(
        self,
        rental_repository: RentalRepository,
        customer_repository: CustomerRepository,
        vehicle_repository: VehicleRepository,
    ) -> None:
        self.rental_repository = rental_repository
        self.customer_repository = customer_repository
        self.vehicle_repository = vehicle_repository

    def create_rental(self, customer_code: str, vehicle_plate: str, pickup_date: date, days: int) -> Rental:
        customer = self.customer_repository.get_by_code(customer_code)

        if customer is None:
            raise NotFoundError("O aluguel exige um cliente cadastrado.")

        vehicle = self.vehicle_repository.get_by_plate(vehicle_plate)

        if vehicle is None:
            raise NotFoundError("O aluguel exige um veículo cadastrado.")
        if not vehicle.is_available or self.rental_repository.has_active_rental_for_vehicle(vehicle.plate):
            raise ConflictError("O veículo não está disponível para aluguel.")

        rental = Rental.create(customer, vehicle, pickup_date, days)

        vehicle.set_rented()
        self.vehicle_repository.update(vehicle)
        return self.rental_repository.insert(rental)

    def finish_rental(self, rental_id: int) -> Rental:
        rental = self.get_rental(rental_id)

        if rental.status != ACTIVE:
            raise ConflictError("O aluguel já está finalizado.")

        vehicle = self.vehicle_repository.get_by_plate(rental.vehicle_plate)

        if vehicle is None:
            raise NotFoundError("Veículo do aluguel não encontrado.")

        rental.set_finished()
        vehicle.set_available()
        self.rental_repository.update(rental)
        self.vehicle_repository.update(vehicle)

        return rental

    def get_rental(self, rental_id: int) -> Rental:
        rental = self.rental_repository.get_by_id(rental_id)

        if rental is None:
            raise NotFoundError("Aluguel não encontrado.")

        return rental

    def list_rentals(self) -> list[Rental]:
        return self.rental_repository.get_all()

    def list_customer_rentals(self, customer_code: str) -> list[Rental]:
        return self.rental_repository.get_by_customer(customer_code)

    def list_active_rentals(self) -> list[Rental]:
        return [rental for rental in self.list_rentals() if rental.status == ACTIVE]

    def calc_late_fee(self, rental_id: int, reference_date: date | None = None) -> float:
        rental = self.get_rental(rental_id)

        if rental.status != ACTIVE:
            return 0.0

        today = reference_date or date.today()

        if today <= rental.expected_return_date:
            return 0.0

        vehicle = self.vehicle_repository.get_by_plate(rental.vehicle_plate)

        if vehicle is None:
            raise NotFoundError("Veículo do aluguel não encontrado.")

        overdue_days = (today - rental.expected_return_date).days
        return round(vehicle.daily_rate * 0.2 * overdue_days, 2)
