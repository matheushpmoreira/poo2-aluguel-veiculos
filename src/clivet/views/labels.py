from clivet.models import AnimalStatus, BookingStatus, CatHairType, DogSize, ServiceType, Species

SPECIES_LABELS = {
    Species.DOG: "cachorro",
    Species.CAT: "gato",
    Species.BIRD: "ave",
}

ANIMAL_STATUS_LABELS = {
    AnimalStatus.ACTIVE: "ativo",
    AnimalStatus.INACTIVE: "inativo",
}

DOG_SIZE_LABELS = {
    DogSize.SMALL: "pequeno",
    DogSize.MEDIUM: "médio",
    DogSize.LARGE: "grande",
}

CAT_HAIR_LABELS = {
    CatHairType.SHORT: "curto",
    CatHairType.LONG: "longo",
}

SERVICE_TYPE_LABELS = {
    ServiceType.CONSULTATION: "consulta veterinária",
    ServiceType.BATH_GROOMING: "banho e tosa",
    ServiceType.VACCINATION: "vacinação",
    ServiceType.EXAM: "exame",
    ServiceType.SURGERY: "cirurgia",
    ServiceType.HOUSING: "hospedagem",
}

BOOKING_STATUS_LABELS = {
    BookingStatus.BOOKED: "agendado",
    BookingStatus.IN_PROGRESS: "em atendimento",
    BookingStatus.COMPLETED: "concluído",
    BookingStatus.CANCELED: "cancelado",
    BookingStatus.MISSED: "faltou",
}


def money(value: float) -> str:
    return f"R$ {value:.2f}"


def species_label(value: Species | str) -> str:
    return SPECIES_LABELS.get(Species(str(value)), str(value))


def animal_status_label(value: AnimalStatus | str) -> str:
    return ANIMAL_STATUS_LABELS.get(AnimalStatus(str(value)), str(value))


def dog_size_label(value: DogSize | str) -> str:
    return DOG_SIZE_LABELS.get(DogSize(str(value)), str(value))


def cat_hair_label(value: CatHairType | str) -> str:
    return CAT_HAIR_LABELS.get(CatHairType(str(value)), str(value))


def service_type_label(value: ServiceType | str) -> str:
    return SERVICE_TYPE_LABELS.get(ServiceType(str(value)), str(value))


def booking_status_label(value: BookingStatus | str) -> str:
    return BOOKING_STATUS_LABELS.get(BookingStatus(str(value)), str(value))
