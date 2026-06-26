from clivet.errors import NotFoundError
from clivet.models import Service
from clivet.repositories import ServiceRepository
from clivet.services.base import BaseService


class ServiceCatalog(BaseService):
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
