from clivet.errors import NotFoundError
from clivet.models import Animal
from clivet.repositories import AnimalRepository, TutorRepository


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
