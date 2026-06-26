from abc import ABC, abstractmethod


class BaseService(ABC):
    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
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
