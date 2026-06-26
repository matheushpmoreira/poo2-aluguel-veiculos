from clivet.errors import NotFoundError
from clivet.models import Tutor
from clivet.repositories import TutorRepository
from clivet.services.base import BaseService


class TutorService(BaseService):
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
