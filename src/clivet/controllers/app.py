from datetime import date, datetime
from typing import Any

from clivet.database import Database
from clivet.errors import BadRequestError, UnprocessableEntityError
from clivet.models import (
    Animal,
    AnimalStatus,
    BathGrooming,
    Bird,
    Booking,
    BookingStatus,
    Cat,
    Consultation,
    Dog,
    Housing,
    Service,
    ServiceType,
    Species,
    Tutor,
    Vaccination,
)
from clivet.repositories import AnimalRepository, BookingRepository, ServiceRepository, TutorRepository
from clivet.services import AnimalService, BookingService, ServiceCatalog, TutorService


class AppController:
    def __init__(self, database: Database) -> None:
        tutor_repository = TutorRepository(database)
        animal_repository = AnimalRepository(database)
        service_repository = ServiceRepository(database)
        booking_repository = BookingRepository(database, animal_repository, service_repository)

        self._tutors = TutorService(tutor_repository)
        self._animals = AnimalService(animal_repository, tutor_repository)
        self._services = ServiceCatalog(service_repository)
        self._bookings = BookingService(booking_repository, animal_repository, service_repository)

    def get_tutors(self) -> list[Tutor]:
        return self._tutors.list()

    def get_tutor(self, cpf: str) -> Tutor:
        return self._tutors.get(cpf)

    def post_tutor(self, data: dict[str, Any]) -> Tutor:
        return self._tutors.create(self._build_tutor(data))

    def put_tutor(self, cpf: str, data: dict[str, Any]) -> Tutor:
        payload = dict(data)
        payload["cpf"] = cpf
        return self._tutors.update(self._build_tutor(payload))

    def delete_tutor(self, cpf: str) -> None:
        self._tutors.delete(cpf)

    def get_animals(self, query: dict[str, Any] | None = None) -> list[Animal]:
        query = query or {}
        return self._animals.list(tutor_cpf=str(query.get("tutor_cpf", "")))

    def get_animal(self, code: str) -> Animal:
        return self._animals.get(code)

    def post_animal(self, data: dict[str, Any]) -> Animal:
        return self._animals.create(self._build_animal(data))

    def put_animal(self, code: str, data: dict[str, Any]) -> Animal:
        payload = dict(data)
        payload["code"] = code
        return self._animals.update(self._build_animal(payload))

    def delete_animal(self, code: str) -> None:
        self._animals.delete(code)

    def get_services(self) -> list[Service]:
        return self._services.list()

    def get_service(self, code: str) -> Service:
        return self._services.get(code)

    def post_service(self, data: dict[str, Any]) -> Service:
        return self._services.create(self._build_service(data))

    def put_service(self, code: str, data: dict[str, Any]) -> Service:
        payload = dict(data)
        payload["code"] = code
        return self._services.update(self._build_service(payload))

    def delete_service(self, code: str) -> None:
        self._services.delete(code)

    def get_bookings(self, query: dict[str, Any] | None = None) -> list[Booking]:
        query = query or {}
        status = self._parse_booking_status(query.get("status")) if query.get("status") else None
        day = self._parse_date(query.get("date"), "data") if query.get("date") else None
        return self._bookings.list(
            animal_code=str(query.get("animal_code", "")),
            status=status,
            day=day,
        )

    def get_booking(self, code: str) -> Booking:
        return self._bookings.get(code)

    def post_booking(self, data: dict[str, Any]) -> Booking:
        return self._bookings.create(
            code=str(data.get("code", "")),
            animal_code=str(data.get("animal_code", "")),
            service_codes=self._parse_service_codes(data.get("service_codes", [])),
            start_at=self._parse_datetime(data.get("start_at"), "início"),
            observations=str(data.get("observations", "")),
        )

    def put_booking(self, code: str, data: dict[str, Any]) -> Booking:
        return self._bookings.update(
            code=code,
            animal_code=str(data.get("animal_code", "")),
            service_codes=self._parse_service_codes(data.get("service_codes", [])),
            start_at=self._parse_datetime(data.get("start_at"), "início"),
            status=self._parse_booking_status(data.get("status", BookingStatus.BOOKED)),
            observations=str(data.get("observations", "")),
        )

    def delete_booking(self, code: str) -> None:
        self._bookings.delete(code)

    def complete_booking(self, code: str) -> Booking:
        return self._bookings.complete(code)

    def cancel_booking(self, code: str) -> Booking:
        return self._bookings.cancel(code)

    def mark_booking_missed(self, code: str) -> Booking:
        return self._bookings.mark_missed(code)

    def get_animal_history(self, animal_code: str) -> list[Booking]:
        return self._bookings.animal_history(animal_code)

    def _build_tutor(self, data: dict[str, Any]) -> Tutor:
        return Tutor(
            cpf=str(data.get("cpf", "")),
            name=str(data.get("name", "")),
            phone=str(data.get("phone", "")),
            email=str(data.get("email", "")),
            address=str(data.get("address", "")),
        )

    def _build_animal(self, data: dict[str, Any]) -> Animal:
        base = {
            "code": str(data.get("code", "")),
            "name": str(data.get("name", "")),
            "species": self._parse_species(data.get("species", "")),
            "breed": str(data.get("breed", "")),
            "birthday": self._parse_date(data.get("birthday"), "nascimento"),
            "weight": self._parse_float(data.get("weight"), "peso"),
            "tutor_cpf": str(data.get("tutor_cpf", "")),
            "status": self._parse_animal_status(data.get("status", AnimalStatus.ACTIVE)),
        }
        if base["species"] == Species.DOG:
            return Dog(
                **base,
                size=str(data.get("dog_size", "medium")),
                rabies_vaccinated=self._parse_bool(data.get("rabies_vaccinated", False)),
            )
        if base["species"] == Species.CAT:
            return Cat(
                **base,
                neutered=self._parse_bool(data.get("cat_neutered", False)),
                hair_type=str(data.get("cat_hair_type", "short")),
            )
        return Bird(
            **base,
            leg_band=str(data.get("bird_leg_band", "")),
            exotic=self._parse_bool(data.get("bird_exotic", False)),
        )

    def _build_service(self, data: dict[str, Any]) -> Service:
        base = {
            "code": str(data.get("code", "")),
            "name": str(data.get("name", "")),
            "service_type": self._parse_service_type(data.get("service_type", "")),
            "description": str(data.get("description", "")),
            "base_value": self._parse_float(data.get("base_value"), "valor base"),
            "duration_minutes": self._parse_int(data.get("duration_minutes"), "duração"),
        }
        if base["service_type"] == ServiceType.CONSULTATION:
            return Consultation(
                **base,
                veterinarian=str(data.get("veterinarian", "")),
                specialty=str(data.get("specialty", "")),
            )
        if base["service_type"] == ServiceType.BATH_GROOMING:
            return BathGrooming(
                **base,
                nail_clipping=self._parse_bool(data.get("nail_clipping", False)),
                perfume=self._parse_bool(data.get("perfume", False)),
            )
        if base["service_type"] == ServiceType.VACCINATION:
            return Vaccination(
                **base,
                batch=str(data.get("batch", "")),
                expiration_date=self._parse_date(data.get("expiration_date"), "validade"),
                laboratory=str(data.get("laboratory", "")),
            )
        if base["service_type"] == ServiceType.HOUSING:
            return Housing(
                **base,
                daily_rate=self._parse_float(data.get("daily_rate", data.get("base_value")), "diária"),
                accommodation_capacity=self._parse_int(data.get("accommodation_capacity", 1), "capacidade"),
            )
        return Service(**base)

    @staticmethod
    def _parse_int(value: Any, field_name: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise BadRequestError(f"{field_name.capitalize()} inválida.") from exc

    @staticmethod
    def _parse_float(value: Any, field_name: str) -> float:
        try:
            return float(str(value).replace(",", "."))
        except (TypeError, ValueError) as exc:
            raise BadRequestError(f"{field_name.capitalize()} inválido.") from exc

    @staticmethod
    def _parse_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "sim", "yes", "on"}

    @staticmethod
    def _parse_date(value: Any, field_name: str) -> date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        try:
            return date.fromisoformat(str(value))
        except (TypeError, ValueError) as exc:
            raise BadRequestError(f"{field_name.capitalize()} inválida. Use AAAA-MM-DD.") from exc

    @staticmethod
    def _parse_datetime(value: Any, field_name: str) -> datetime:
        if isinstance(value, datetime):
            return value
        text = str(value).strip().replace(" ", "T")
        try:
            return datetime.fromisoformat(text)
        except (TypeError, ValueError) as exc:
            raise BadRequestError(f"{field_name.capitalize()} inválido. Use AAAA-MM-DD HH:MM.") from exc

    @staticmethod
    def _parse_service_codes(value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        try:
            return [str(item).strip() for item in value if str(item).strip()]
        except TypeError as exc:
            raise BadRequestError("Lista de serviços inválida.") from exc

    @staticmethod
    def _parse_species(value: Any) -> Species:
        try:
            return Species(str(value).strip().lower())
        except (TypeError, ValueError) as exc:
            raise UnprocessableEntityError("A espécie deve ser cachorro, gato ou ave.") from exc

    @staticmethod
    def _parse_animal_status(value: Any) -> AnimalStatus:
        try:
            return AnimalStatus(str(value).strip().lower())
        except (TypeError, ValueError) as exc:
            raise UnprocessableEntityError("O status do animal deve ser ativo ou inativo.") from exc

    @staticmethod
    def _parse_service_type(value: Any) -> ServiceType:
        try:
            return ServiceType(str(value).strip().lower())
        except (TypeError, ValueError) as exc:
            raise UnprocessableEntityError("O tipo de serviço é inválido.") from exc

    @staticmethod
    def _parse_booking_status(value: Any) -> BookingStatus:
        try:
            return BookingStatus(str(value).strip().lower())
        except (TypeError, ValueError) as exc:
            raise UnprocessableEntityError("O status do agendamento é inválido.") from exc
