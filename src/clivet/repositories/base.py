from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def insert(self, entity) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, identifier: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, identifier: str):
        raise NotImplementedError

    @abstractmethod
    def list(self, *args, **kwargs):
        raise NotImplementedError
