import tkinter as tk
from tkinter import ttk

from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController
from matheushpmoreira.vehicle_rental_system.backend.models import Vehicle, VehicleStatus
from matheushpmoreira.vehicle_rental_system.frontend.admin.forms import VehicleForm
from matheushpmoreira.vehicle_rental_system.frontend.base import BaseFrame
from matheushpmoreira.vehicle_rental_system.frontend.form import ChoiceFieldSpec, Choice, SelectInput
from matheushpmoreira.vehicle_rental_system.frontend.formatters import vehicle_admin_row
from matheushpmoreira.vehicle_rental_system.frontend.labels import vehicle_status_label
from matheushpmoreira.vehicle_rental_system.frontend.tables import Column, DataTable


class VehicleAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.search_text = tk.StringVar()
        self.form: VehicleForm
        self.status_filter: SelectInput
        self.table: DataTable[Vehicle]
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        form_area = ttk.Frame(container)
        form_area.pack(side="left", fill="y", padx=(0, 10))

        self.form = VehicleForm(form_area)
        self.form.pack(fill="x")
        self.form.add_action_buttons(
            (
                ("Cadastrar", self.create_vehicle),
                ("Atualizar", self.update_vehicle),
                ("Remover", self.delete_vehicle),
                ("Limpar", self.clear_form),
            )
        )

        list_area = ttk.Frame(container)
        list_area.pack(side="left", fill="both", expand=True)

        filters = ttk.Frame(list_area)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Entry(filters, textvariable=self.search_text).pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.status_filter = SelectInput(
            filters,
            ChoiceFieldSpec(
                "status",
                "Situação",
                (Choice("", ""), *(Choice(status.value, vehicle_status_label(status)) for status in VehicleStatus)),
                width=14,
            ),
        )
        self.status_filter.pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Buscar", command=self.refresh).pack(side="left")

        self.table = DataTable(
            list_area,
            (
                Column("plate", "Placa", 90),
                Column("brand", "Marca", 120),
                Column("model", "Modelo", 140),
                Column("year", "Ano", 70),
                Column("type", "Tipo", 110),
                Column("rate", "Diária", 90),
                Column("status", "Situação", 90),
            ),
            vehicle_admin_row,
        )
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.fill_from_selection)

    def create_vehicle(self) -> None:
        try:
            self.controller.post_vehicle(self.form.payload())
            self.show_success("Veículo cadastrado.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update_vehicle(self) -> None:
        try:
            self.controller.put_vehicle(self.form.plate(), self.form.payload())
            self.show_success("Veículo atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete_vehicle(self) -> None:
        try:
            self.controller.delete_vehicle(self.form.plate())
            self.show_success("Veículo removido.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.table.set_items(
            self.controller.get_vehicles({"q": self.search_text.get(), "status": self.status_filter.get_value()})
        )

    def fill_from_selection(self, _event: tk.Event) -> None:
        vehicle = self.table.selected_item()
        if vehicle is not None:
            self.form.set_vehicle(vehicle)

    def clear_form(self) -> None:
        self.form.clear()
