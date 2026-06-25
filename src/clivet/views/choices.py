from clivet.models import (
    Animal,
    AnimalStatus,
    BookingStatus,
    CatHairType,
    DogSize,
    Service,
    ServiceType,
    Species,
    Tutor,
)
from clivet.views.labels import (
    animal_status_label,
    booking_status_label,
    cat_hair_label,
    dog_size_label,
    service_type_label,
    species_label,
)
from clivet.views.widgets import Choice


def species_choices() -> tuple[Choice[Species], ...]:
    return tuple(Choice(value, species_label(value)) for value in Species)


def animal_status_choices() -> tuple[Choice[AnimalStatus], ...]:
    return tuple(Choice(value, animal_status_label(value)) for value in AnimalStatus)


def dog_size_choices() -> tuple[Choice[DogSize], ...]:
    return tuple(Choice(value, dog_size_label(value)) for value in DogSize)


def cat_hair_choices() -> tuple[Choice[CatHairType], ...]:
    return tuple(Choice(value, cat_hair_label(value)) for value in CatHairType)


def service_type_choices() -> tuple[Choice[ServiceType], ...]:
    return tuple(Choice(value, service_type_label(value)) for value in ServiceType)


def booking_status_choices(include_empty: bool = False) -> tuple[Choice[BookingStatus | None], ...]:
    choices: tuple[Choice[BookingStatus | None], ...] = tuple(
        Choice(value, booking_status_label(value)) for value in BookingStatus
    )
    if include_empty:
        return (Choice(None, ""),) + choices
    return choices


def tutor_choices(tutors: list[Tutor], include_empty: bool = False) -> tuple[Choice[str], ...]:
    choices = tuple(Choice(tutor.cpf, f"{tutor.cpf} - {tutor.name}") for tutor in tutors)
    if include_empty:
        return (Choice("", ""),) + choices
    return choices


def animal_choices(animals: list[Animal], include_empty: bool = False) -> tuple[Choice[str], ...]:
    choices = tuple(Choice(animal.code, f"{animal.code} - {animal.name}") for animal in animals)
    if include_empty:
        return (Choice("", ""),) + choices
    return choices


def service_choices(services: list[Service]) -> tuple[Choice[str], ...]:
    return tuple(Choice(service.code, f"{service.code} - {service.name}") for service in services)
