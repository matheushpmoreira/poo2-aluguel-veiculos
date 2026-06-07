import tkinter as tk
from tkinter import ttk

from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController
from matheushpmoreira.vehicle_rental_system.backend.models import Customer
from matheushpmoreira.vehicle_rental_system.frontend.admin.forms import CustomerForm
from matheushpmoreira.vehicle_rental_system.frontend.base import BaseFrame
from matheushpmoreira.vehicle_rental_system.frontend.formatters import customer_admin_row
from matheushpmoreira.vehicle_rental_system.frontend.tables import Column, DataTable


class CustomerAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.form: CustomerForm
        self.table: DataTable[Customer]
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        form_area = ttk.Frame(container)
        form_area.pack(side="left", fill="y", padx=(0, 10))

        self.form = CustomerForm(form_area)
        self.form.pack(fill="x")
        self.form.add_action_buttons(
            (
                ("Cadastrar", self.create_customer),
                ("Atualizar", self.update_customer),
                ("Remover", self.delete_customer),
                ("Limpar", self.clear_form),
            )
        )

        self.table = DataTable(
            container,
            (
                Column("code", "Código", 110),
                Column("name", "Nome", 160),
                Column("phone", "Telefone", 110),
                Column("email", "E-mail", 180),
                Column("address", "Endereço", 220),
                Column("password", "Senha", 100),
            ),
            customer_admin_row,
        )
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.fill_from_selection)

    def create_customer(self) -> None:
        try:
            self.controller.post_customer(self.form.payload())
            self.show_success("Cliente cadastrado.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update_customer(self) -> None:
        try:
            self.controller.put_customer(self.form.code(), self.form.payload())
            self.show_success("Cliente atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete_customer(self) -> None:
        try:
            self.controller.delete_customer(self.form.code())
            self.show_success("Cliente removido.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.table.set_items(self.controller.get_customers())

    def fill_from_selection(self, _event: tk.Event) -> None:
        customer = self.table.selected_item()
        if customer is not None:
            self.form.set_customer(customer)

    def clear_form(self) -> None:
        self.form.clear()
