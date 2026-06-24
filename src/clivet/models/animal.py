from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from clivet.errors import UnprocessableEntityError


class Species(StrEnum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"


class AnimalStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DogSize(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class CatHairType(StrEnum):
    SHORT = "short"
    LONG = "long"


@dataclass
class Animal:
    code: str
    name: str
    species: Species
    breed: str
    birthday: date
    weight: float
    tutor_cpf: str
    status: AnimalStatus = AnimalStatus.ACTIVE

    def __post_init__(self) -> None:
        self.code = self.code.strip().upper()
        self.name = self.name.strip()
        self.breed = self.breed.strip()
        self.tutor_cpf = self.tutor_cpf.strip()
        try:
            self.species = Species(str(self.species).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("A espécie deve ser cachorro, gato ou ave.") from exc
        try:
            self.status = AnimalStatus(str(self.status).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("O status do animal deve ser ativo ou inativo.") from exc

        if not self.code or not self.name or not self.tutor_cpf:
            raise UnprocessableEntityError("Código, nome e tutor do animal são obrigatórios.")
        if self.weight <= 0:
            raise UnprocessableEntityError("O peso do animal deve ser maior que zero.")
        if self.birthday > date.today():
            raise UnprocessableEntityError("A data de nascimento do animal não pode estar no futuro.")

    @property
    def is_active(self) -> bool:
        return self.status == AnimalStatus.ACTIVE


@dataclass
class Dog(Animal):
    size: DogSize = DogSize.MEDIUM
    rabies_vaccinated: bool = False

    def __post_init__(self) -> None:
        self.species = Species.DOG
        super().__post_init__()
        try:
            self.size = DogSize(str(self.size).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("O porte do cachorro deve ser pequeno, médio ou grande.") from exc


@dataclass
class Cat(Animal):
    neutered: bool = False
    hair_type: CatHairType = CatHairType.SHORT

    def __post_init__(self) -> None:
        self.species = Species.CAT
        super().__post_init__()
        try:
            self.hair_type = CatHairType(str(self.hair_type).strip().lower())
        except ValueError as exc:
            raise UnprocessableEntityError("O tipo de pelo do gato deve ser curto ou longo.") from exc


@dataclass
class Bird(Animal):
    leg_band: str = ""
    exotic: bool = False

    def __post_init__(self) -> None:
        self.species = Species.BIRD
        super().__post_init__()
        self.leg_band = self.leg_band.strip()
