import tkinter as tk
from tkinter import ttk

from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController
from matheushpmoreira.vehicle_rental_system.backend.models import Rental
from matheushpmoreira.vehicle_rental_system.frontend.admin.forms import RentalForm
from matheushpmoreira.vehicle_rental_system.frontend.base import BaseFrame
from matheushpmoreira.vehicle_rental_system.frontend.formatters import (
    available_vehicle_filter,
    rental_admin_row,
)
from matheushpmoreira.vehicle_rental_system.frontend.tables import Column, DataTable


class RentalAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.form: RentalForm
        self.table: DataTable[Rental]
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        form_area = ttk.Frame(container)
        form_area.pack(side="left", fill="y", padx=(0, 10))

        self.form = RentalForm(form_area)
        self.form.pack(fill="x")
        self.form.add_action_buttons(
            (
                ("Criar aluguel", self.create_rental),
                ("Finalizar aluguel selecionado", self.finish_selected),
            )
        )

        self.table = DataTable(
            container,
            (
                Column("id", "ID", 60),
                Column("customer", "Cliente", 120),
                Column("vehicle", "Veículo", 100),
                Column("pickup", "Retirada", 100),
                Column("return", "Devolução prevista", 120),
                Column("days", "Dias", 70),
                Column("total", "Total", 90),
                Column("status", "Situação", 90),
            ),
            rental_admin_row,
        )
        self.table.pack(side="left", fill="both", expand=True)

    def create_rental(self) -> None:
        try:
            rental = self.controller.post_rental(self.form.payload())
            self.show_success(f"Aluguel {rental.rental_id} criado. Total: {rental.total_amount:.2f}")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def finish_selected(self) -> None:
        rental = self.table.selected_item()
        if rental is None or rental.rental_id is None:
            self.show_warning("Seleção obrigatória", "Selecione um aluguel primeiro.")
            return
        try:
            self.controller.post_rental_finish(rental.rental_id)
            self.show_success("Aluguel finalizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.form.set_customers(self.controller.get_customers())
        self.form.set_available_vehicles(self.controller.get_vehicles(available_vehicle_filter()))
        self.table.set_items(self.controller.get_rentals())
