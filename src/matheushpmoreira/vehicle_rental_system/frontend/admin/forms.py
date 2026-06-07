import tkinter as tk
from datetime import date

from matheushpmoreira.vehicle_rental_system.backend.models import Customer, Vehicle, VehicleStatus, VehicleType
from matheushpmoreira.vehicle_rental_system.frontend.form import ChoiceFieldSpec, FormFrame, Choice, TextFieldSpec, \
    TextInput, SelectInput
from matheushpmoreira.vehicle_rental_system.frontend.formatters import (
    money,
    customer_payload,
    rental_payload,
    vehicle_admin_payload,
)
from matheushpmoreira.vehicle_rental_system.frontend.labels import vehicle_status_label, vehicle_type_label


class VehicleForm(FormFrame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(
            parent,
            title="Cadastro de veículo",
            inputs={
                "plate": TextInput(self, label="Placa"),
                "brand": TextInput(self, label="Marca"),
                "model": TextInput(self, label="Modelo"),
                "year": TextInput(self, label="Ano"),
                "vehicle_type": SelectInput(
                    self,
                    label="Tipo",
                    choices=tuple(Choice(vehicle_type.value, vehicle_type_label(vehicle_type)) for vehicle_type in VehicleType)
                ),
                "daily_rate": TextInput(self, label="Valor da diária"),
                "status": SelectInput(
                    self,
                    label="Situação",
                    choices=tuple(Choice(status.value, vehicle_status_label(status)) for status in VehicleStatus)
                ),
            },
            buttons=(
                ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2),
                ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2),
                ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2),
                ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2),
            )
        )

    def plate(self) -> str:
        return self.input_value("plate")

    def payload(self) -> dict[str, str]:
        return vehicle_admin_payload(
            self.get_values(),
            self.input_value("vehicle_type"),
            self.input_value("status"),
        )

    def set_vehicle(self, vehicle: Vehicle) -> None:
        self.set_values(
            {
                "plate": vehicle.plate,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "year": vehicle.year,
                "daily_rate": f"{vehicle.daily_rate:.2f}",
            }
        )
        self.set_input_value("vehicle_type", vehicle.vehicle_type.value)
        self.set_input_value("status", vehicle.status.value)


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
        return self.input_value("code")

    def payload(self) -> dict[str, str]:
        return customer_payload(self.get_values())

    def set_customer(self, customer: Customer) -> None:
        self.set_values(
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
        self.set_choice_options(
            "customer_code",
            tuple(Choice(customer.code, f"{customer.code} - {customer.name}") for customer in customers),
        )

    def set_available_vehicles(self, vehicles: list[Vehicle]) -> None:
        self.set_choice_options(
            "vehicle_plate",
            tuple(
                Choice(vehicle.plate, f"{vehicle.plate} - {vehicle.brand} {vehicle.model} ({money(vehicle.daily_rate)})")
                for vehicle in vehicles
            ),
        )

    def payload(self) -> dict[str, str]:
        return rental_payload(
            self.input_value("customer_code"),
            self.input_value("vehicle_plate"),
            self.input_value("pickup_date"),
            self.input_value("days"),
        )
