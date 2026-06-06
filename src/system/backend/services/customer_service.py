from __future__ import annotations

import sqlite3

from system.backend.errors import ConflictError, NotFoundError, UnauthorizedError
from system.backend.models.customer import Customer
from system.backend.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    def create_customer(self, code: str, name: str, phone: str, email: str, address: str, password: str) -> Customer:
        customer = Customer(code, name, phone, email, address, password)

        try:
            self.customer_repository.insert(customer)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Já existe um cliente com este código.") from exc

        return customer

    def update_customer(self, code: str, name: str, phone: str, email: str, address: str, password: str) -> Customer:
        customer = Customer(code, name, phone, email, address, password)
        self.customer_repository.update(customer)
        return customer

    def delete_customer(self, code: str) -> None:
        try:
            self.customer_repository.delete(code)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("O cliente possui histórico de aluguel e não pode ser removido.") from exc

    def get_customer(self, code: str) -> Customer:
        customer = self.customer_repository.get_by_code(code)

        if customer is None:
            raise NotFoundError("Cliente não encontrado.")

        return customer

    def list_customers(self) -> list[Customer]:
        return self.customer_repository.get_all()

    def login(self, code: str, password: str) -> Customer:
        customer = self.get_customer(code)

        if not customer.check_password(password):
            raise UnauthorizedError("Código do cliente ou senha inválidos.")

        return customer
