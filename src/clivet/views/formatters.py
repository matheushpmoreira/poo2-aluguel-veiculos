from clivet.models import Animal, Bird, Booking, Cat, Consultation, Dog, Housing, Service, Vaccination
from clivet.views.labels import animal_status_label, booking_status_label, money, service_type_label, species_label


def bool_label(value: bool) -> str:
    return "sim" if value else "não"


def animal_row(animal: Animal) -> tuple[object, ...]:
    return (
        animal.code,
        animal.name,
        species_label(animal.species),
        animal.breed,
        animal.birthday.isoformat(),
        f"{animal.weight:.2f}",
        animal.tutor_cpf,
        animal_status_label(animal.status),
    )


def animal_details(animal: Animal) -> str:
    if isinstance(animal, Dog):
        return f"Porte: {animal.size.value}; raiva: {bool_label(animal.rabies_vaccinated)}"
    if isinstance(animal, Cat):
        return f"Castrado: {bool_label(animal.neutered)}; pelo: {animal.hair_type.value}"
    if isinstance(animal, Bird):
        return f"Anilha: {animal.leg_band}; exótica: {bool_label(animal.exotic)}"
    return ""


def service_row(service: Service) -> tuple[object, ...]:
    return (
        service.code,
        service.name,
        service_type_label(service.service_type),
        money(service.base_value),
        service.duration_minutes,
        service_details(service),
    )


def service_details(service: Service) -> str:
    if isinstance(service, Consultation):
        return f"{service.veterinarian} - {service.specialty}"
    if isinstance(service, Vaccination):
        return f"{service.laboratory}; lote {service.batch}; validade {service.expiration_date.isoformat()}"
    if isinstance(service, Housing):
        return f"Diária {money(service.daily_rate)}; capacidade {service.accommodation_capacity}"
    return ""


def booking_row(booking: Booking) -> tuple[object, ...]:
    return (
        booking.code,
        booking.animal_code,
        ", ".join(booking.service_codes),
        booking.start_at.strftime("%Y-%m-%d %H:%M"),
        booking.end_at.strftime("%Y-%m-%d %H:%M"),
        money(booking.total_value),
        booking_status_label(booking.status),
    )
