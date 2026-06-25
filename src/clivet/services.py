from datetime import date, datetime

from clivet.errors import ConflictError, NotFoundError, UnprocessableEntityError
from clivet.models import Animal, AnimalStatus, Booking, BookingStatus, Consultation, Service, ServiceType, Tutor
from clivet.repositories import AnimalRepository, BookingRepository, ServiceRepository, TutorRepository


class TutorService:
    def __init__(self, repository: TutorRepository) -> None:
        self.repository = repository

    def create(self, tutor: Tutor) -> Tutor:
        self.repository.insert(tutor)
        return tutor

    def update(self, tutor: Tutor) -> Tutor:
        self.repository.update(tutor)
        return tutor

    def delete(self, cpf: str) -> None:
        self.repository.delete(cpf)

    def get(self, cpf: str) -> Tutor:
        tutor = self.repository.get(cpf)
        if tutor is None:
            raise NotFoundError("Tutor não encontrado.")
        return tutor

    def list(self) -> list[Tutor]:
        return self.repository.list()


class AnimalService:
    def __init__(self, animal_repository: AnimalRepository, tutor_repository: TutorRepository) -> None:
        self.animal_repository = animal_repository
        self.tutor_repository = tutor_repository

    def create(self, animal: Animal) -> Animal:
        self._require_tutor(animal.tutor_cpf)
        self.animal_repository.insert(animal)
        return animal

    def update(self, animal: Animal) -> Animal:
        self._require_tutor(animal.tutor_cpf)
        self.animal_repository.update(animal)
        return animal

    def delete(self, code: str) -> None:
        self.animal_repository.delete(code)

    def get(self, code: str) -> Animal:
        animal = self.animal_repository.get(code)
        if animal is None:
            raise NotFoundError("Animal não encontrado.")
        return animal

    def list(self, tutor_cpf: str = "") -> list[Animal]:
        return self.animal_repository.list(tutor_cpf=tutor_cpf)

    def _require_tutor(self, cpf: str) -> None:
        if self.tutor_repository.get(cpf) is None:
            raise NotFoundError("O animal exige um tutor cadastrado.")


class ServiceCatalog:
    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    def create(self, service: Service) -> Service:
        self.repository.insert(service)
        return service

    def update(self, service: Service) -> Service:
        self.repository.update(service)
        return service

    def delete(self, code: str) -> None:
        self.repository.delete(code)

    def get(self, code: str) -> Service:
        service = self.repository.get(code)
        if service is None:
            raise NotFoundError("Serviço não encontrado.")
        return service

    def list(self) -> list[Service]:
        return self.repository.list()


class BookingService:
    def __init__(
        self,
        booking_repository: BookingRepository,
        animal_repository: AnimalRepository,
        service_repository: ServiceRepository,
    ) -> None:
        self.booking_repository = booking_repository
        self.animal_repository = animal_repository
        self.service_repository = service_repository

    def create(self, code: str, animal_code: str, service_codes: list[str], start_at: datetime, observations: str) -> Booking:
        animal = self._require_animal(animal_code)
        services = self._require_services(service_codes)
        booking = Booking.create(
            code=code, animal=animal, services=services, start_at=start_at, observations=observations
        )
        self._validate_booking(booking)
        self.booking_repository.insert(booking)
        return booking

    def update(
        self,
        code: str,
        animal_code: str,
        service_codes: list[str],
        start_at: datetime,
        status: BookingStatus,
        observations: str,
    ) -> Booking:
        self.get(code)
        animal = self._require_animal(animal_code)
        services = self._require_services(service_codes)
        booking = Booking.create(
            code=code,
            animal=animal,
            services=services,
            start_at=start_at,
            observations=observations,
            status=status,
        )
        self._validate_booking(booking, ignore_code=code)
        self.booking_repository.update(booking)
        return booking

    def delete(self, code: str) -> None:
        self.booking_repository.delete(code)

    def get(self, code: str) -> Booking:
        booking = self.booking_repository.get(code)
        if booking is None:
            raise NotFoundError("Agendamento não encontrado.")
        return booking

    def list(
        self,
        animal_code: str = "",
        status: BookingStatus | None = None,
        day: date | None = None,
    ) -> list[Booking]:
        return self.booking_repository.list(animal_code=animal_code, status=status, day=day)

    def animal_history(self, animal_code: str) -> list[Booking]:
        self._require_animal(animal_code)
        return self.booking_repository.list(animal_code=animal_code)

    def complete(self, code: str) -> Booking:
        booking = self.get(code)
        if booking.status in (BookingStatus.CANCELED, BookingStatus.MISSED):
            raise ConflictError("Agendamentos cancelados ou faltantes não podem ser concluídos.")
        return self.booking_repository.update_status(code, BookingStatus.COMPLETED)

    def cancel(self, code: str) -> Booking:
        return self.booking_repository.update_status(code, BookingStatus.CANCELED)

    def mark_missed(self, code: str) -> Booking:
        return self.booking_repository.update_status(code, BookingStatus.MISSED)

    def _require_animal(self, code: str) -> Animal:
        animal = self.animal_repository.get(code)
        if animal is None:
            raise NotFoundError("O agendamento exige um animal cadastrado.")
        return animal

    def _require_services(self, codes: list[str]) -> list[Service]:
        normalized = [code.strip().upper() for code in codes if code.strip()]
        if not normalized:
            raise UnprocessableEntityError("Selecione pelo menos um serviço.")
        services = self.service_repository.get_many(normalized)
        found = {service.code for service in services}
        missing = [code for code in normalized if code not in found]
        if missing:
            raise NotFoundError(f"Serviço não encontrado: {', '.join(missing)}.")
        return services

    def _validate_booking(self, booking: Booking, ignore_code: str = "") -> None:
        if booking.status not in (BookingStatus.CANCELED, BookingStatus.MISSED):
            animal = booking.animal or self._require_animal(booking.animal_code)
            if animal.status != AnimalStatus.ACTIVE:
                raise ConflictError("Animais inativos não podem ser agendados.")

        overlaps = self.booking_repository.list_overlapping(booking.start_at, booking.end_at, ignore_code=ignore_code)
        for existing in overlaps:
            if existing.animal_code == booking.animal_code:
                raise ConflictError("O animal já possui agendamento neste horário.")

        new_veterinarians = self._consultation_veterinarians(booking.services)
        if not new_veterinarians:
            return
        for existing in overlaps:
            existing_veterinarians = self._consultation_veterinarians(existing.services)
            repeated = sorted(new_veterinarians & existing_veterinarians)
            if repeated:
                raise ConflictError(f"Veterinário indisponível neste horário: {', '.join(repeated)}.")

    @staticmethod
    def _consultation_veterinarians(services: list[Service]) -> set[str]:
        return {
            service.veterinarian.strip().casefold()
            for service in services
            if service.service_type == ServiceType.CONSULTATION
            and isinstance(service, Consultation)
            and service.veterinarian.strip()
        }

