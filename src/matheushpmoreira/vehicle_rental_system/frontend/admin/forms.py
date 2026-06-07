import tkinter as tk
from datetime import date

from matheushpmoreira.vehicle_rental_system.backend.models import Customer, Vehicle
from matheushpmoreira.vehicle_rental_system.frontend.choices import (
    vehicle_status_choices,
    vehicle_type_choices,
)
from matheushpmoreira.vehicle_rental_system.frontend.form import ChoiceFieldSpec, FormFrame, TextFieldSpec
from matheushpmoreira.vehicle_rental_system.frontend.formatters import (
    available_vehicle_choices,
    customer_choices,
    customer_payload,
    rental_payload,
    vehicle_admin_payload,
)


class VehicleForm(FormFrame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(
            parent,
            "Cadastro de veículo",
            (
                TextFieldSpec("plate", "Placa"),
                TextFieldSpec("brand", "Marca"),
                TextFieldSpec("model", "Modelo"),
                TextFieldSpec("year", "Ano"),
                ChoiceFieldSpec("vehicle_type", "Tipo", vehicle_type_choices()),
                TextFieldSpec("daily_rate", "Valor da diária"),
                ChoiceFieldSpec("status", "Situação", vehicle_status_choices()),
            ),
        )

    def plate(self) -> str:
        return self.text_value("plate")

    def payload(self) -> dict[str, str]:
        return vehicle_admin_payload(
            self.text_values(),
            self.require_choice("vehicle_type"),
            self.require_choice("status"),
        )

    def set_vehicle(self, vehicle: Vehicle) -> None:
        self.set_text_values(
            {
                "plate": vehicle.plate,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "year": vehicle.year,
                "daily_rate": f"{vehicle.daily_rate:.2f}",
            }
        )
        self.select_choice("vehicle_type", vehicle.vehicle_type.value)
        self.select_choice("status", vehicle.status.value)


class CustomerForm(FormFrame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(
            parent,
            "Cadastro de cliente",
            (
                TextFieldSpec("code", "Código ou CPF"),
                TextFieldSpec("name", "Nome"),
                TextFieldSpec("phone", "Telefone"),
                TextFieldSpec("email", "E-mail"),
                TextFieldSpec("address", "Endereço"),
                TextFieldSpec("password", "Senha"),
            ),
        )

    def code(self) -> str:
        return self.text_value("code")

    def payload(self) -> dict[str, str]:
        return customer_payload(self.text_values())

    def set_customer(self, customer: Customer) -> None:
        self.set_text_values(
            {
                "code": customer.code,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "password": customer.password,
            }
        )


class RentalForm(FormFrame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(
            parent,
            "Criar aluguel",
            (
                ChoiceFieldSpec("customer_code", "Cliente", (), width=34),
                ChoiceFieldSpec("vehicle_plate", "Veículo", (), width=34),
                TextFieldSpec("pickup_date", "Data de retirada", default=date.today().isoformat()),
                TextFieldSpec("days", "Dias", default="1"),
            ),
        )

    def set_customers(self, customers: list[Customer]) -> None:
        self.set_choice_options("customer_code", customer_choices(customers))

    def set_available_vehicles(self, vehicles: list[Vehicle]) -> None:
        self.set_choice_options("vehicle_plate", available_vehicle_choices(vehicles))

    def payload(self) -> dict[str, str]:
        return rental_payload(
            self.require_choice("customer_code"),
            self.require_choice("vehicle_plate"),
            self.text_value("pickup_date"),
            self.text_value("days"),
        )
