from __future__ import annotations

import csv
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, ttk

from system.backend.controllers import AppController
from system.backend.models import Rental, Vehicle, VehicleStatus

from .base import Action, BaseFrame
from .choices import ChoiceBox, vehicle_status_choices, vehicle_status_filter_choices, vehicle_type_choices
from .form import VehicleForm
from .formatters import (
    active_rental_filter,
    available_vehicle_choices,
    available_vehicle_filter,
    customer_choices,
    customer_payload,
    customer_row,
    rental_admin_row,
    rental_payload,
    report_csv_rows,
    report_rental_row,
    report_vehicle_row,
    vehicle_admin_payload,
    vehicle_admin_row,
)
from .tables import Column, DataTable


class AdminPanel(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)

        # Cabeçalho
        header = ttk.Label(self, text="Operações administrativas", style="Title.TLabel")
        header.pack(anchor="w", pady=(0, 8))

        # Subpainéis
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        self.vehicle_frame = VehicleAdminFrame(notebook, controller)
        self.customer_frame = CustomerAdminFrame(notebook, controller)
        self.rental_frame = RentalAdminFrame(notebook, controller)
        self.report_frame = ReportFrame(notebook, controller)
        notebook.add(self.vehicle_frame, text="Veículos")
        notebook.add(self.customer_frame, text="Clientes")
        notebook.add(self.rental_frame, text="Aluguéis")
        notebook.add(self.report_frame, text="Relatórios")

        # TODO: dá p remover?
        notebook.bind("<<NotebookTabChanged>>", self._refresh_current_tab)

    def _refresh_current_tab(self, _event: tk.Event) -> None:
        for frame in (self.vehicle_frame, self.customer_frame, self.rental_frame, self.report_frame):
            frame.refresh()


class VehicleAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.fields = {field: tk.StringVar() for field in ("plate", "brand", "model", "year", "daily_rate")}
        self.search_text = tk.StringVar()
        self.type_choice: ChoiceBox
        self.status_choice: ChoiceBox
        self.status_filter: ChoiceBox
        self.table: DataTable[Vehicle]
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Formulário
        # form = VehicleForm(container, self.controller)
        form = ttk.LabelFrame(container, text="Cadastro de veículo", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))
        self._entry(form, "Placa", "plate", 0)
        self._entry(form, "Marca", "brand", 1)
        self._entry(form, "Modelo", "model", 2)
        self._entry(form, "Ano", "year", 3)
        ttk.Label(form, text="Tipo").grid(row=4, column=0, sticky="w", pady=3)
        self.type_choice = ChoiceBox(form, vehicle_type_choices())
        self.type_choice.grid(row=4, column=1, sticky="ew", pady=3)
        self._entry(form, "Valor da diária", "daily_rate", 5)
        ttk.Label(form, text="Situação").grid(row=6, column=0, sticky="w", pady=3)
        self.status_choice = ChoiceBox(form, vehicle_status_choices())
        self.status_choice.grid(row=6, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)

        # Botões
        buttons = ttk.Frame(form)
        buttons.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        # Action("Cadastrar", self.create_vehicle, buttons)
        # Action("Atualizar", self.update_vehicle, buttons)
        # Action("Remover", self.delete_vehicle, buttons)
        # Action("Limpar", self.clear_form, buttons)
        actions = (
            Action("Cadastrar", self.create_vehicle),
            Action("Atualizar", self.update_vehicle),
            Action("Remover", self.delete_vehicle),
            Action("Limpar", self.clear_form),
        )

        for action in actions:
            action.pack_button(buttons)

        # pack_action_buttons(
        #     buttons,
        #     (
        #         Action("Cadastrar", self.create_vehicle),
        #         Action("Atualizar", self.update_vehicle),
        #         Action("Remover", self.delete_vehicle),
        #         Action("Limpar", self.clear_form),
        #     ),
        # )

        list_area = ttk.Frame(container)
        list_area.pack(side="left", fill="both", expand=True)
        filters = ttk.Frame(list_area)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Entry(filters, textvariable=self.search_text).pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.status_filter = ChoiceBox(filters, vehicle_status_filter_choices(), width=14)
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

    def _entry(self, parent: ttk.Frame, label: str, key: str, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.fields[key]).grid(row=row, column=1, sticky="ew", pady=3)

    def create_vehicle(self) -> None:
        try:
            self.controller.post_vehicle(self._payload())
            self.show_success("Veículo cadastrado.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update_vehicle(self) -> None:
        try:
            self.controller.put_vehicle(self.fields["plate"].get(), self._payload())
            self.show_success("Veículo atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete_vehicle(self) -> None:
        try:
            self.controller.delete_vehicle(self.fields["plate"].get())
            self.show_success("Veículo removido.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        status = self.status_filter.selected_value()
        vehicles = self.controller.get_vehicles(
            {"q": self.search_text.get(), "status": status.value if isinstance(status, VehicleStatus) else ""}
        )
        self.table.set_items(vehicles)

    def fill_from_selection(self, _event: tk.Event) -> None:
        vehicle = self.table.selected_item()
        if vehicle is None:
            return
        self.fields["plate"].set(vehicle.plate)
        self.fields["brand"].set(vehicle.brand)
        self.fields["model"].set(vehicle.model)
        self.fields["year"].set(str(vehicle.year))
        self.fields["daily_rate"].set(f"{vehicle.daily_rate:.2f}")
        self.type_choice.select_value(vehicle.vehicle_type)
        self.status_choice.select_value(vehicle.status)

    def clear_form(self) -> None:
        for variable in self.fields.values():
            variable.set("")
        self.type_choice.select_first()
        self.status_choice.select_first()

    def _payload(self) -> dict[str, str]:
        fields = {key: variable.get() for key, variable in self.fields.items()}
        return vehicle_admin_payload(fields, self.type_choice.require_value(), self.status_choice.require_value())


class CustomerAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.fields = {
            "code": tk.StringVar(),
            "name": tk.StringVar(),
            "phone": tk.StringVar(),
            "email": tk.StringVar(),
            "address": tk.StringVar(),
            "password": tk.StringVar(),
        }
        self.table = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Formulário
        # form = CustomerForm(container, self.controller)
        form = ttk.LabelFrame(container, text="Cadastro de cliente", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))
        for row, (key, label) in enumerate(
            (
                ("code", "Código ou CPF"),
                ("name", "Nome"),
                ("phone", "Telefone"),
                ("email", "E-mail"),
                ("address", "Endereço"),
                ("password", "Senha"),
            )
        ):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=self.fields[key]).grid(row=row, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(form)
        buttons.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        actions = (
            Action("Cadastrar", self.create_customer),
            Action("Atualizar", self.update_customer),
            Action("Remover", self.delete_customer),
            Action("Limpar", self.clear_form),
        )

        for action in actions:
            action.pack_button(buttons)
        # pack_action_buttons(
        #     buttons,
        #     (
        #         Action("Cadastrar", self.create_customer),
        #         Action("Atualizar", self.update_customer),
        #         Action("Remover", self.delete_customer),
        #         Action("Limpar", self.clear_form),
        #     ),
        # )

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
            customer_row,
        )
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.fill_from_selection)

    def create_customer(self) -> None:
        try:
            self.controller.post_customer(self._payload())
            self.show_success("Cliente cadastrado.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update_customer(self) -> None:
        try:
            self.controller.put_customer(self.fields["code"].get(), self._payload())
            self.show_success("Cliente atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete_customer(self) -> None:
        try:
            self.controller.delete_customer(self.fields["code"].get())
            self.show_success("Cliente removido.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.table.set_items(self.controller.get_customers())

    def fill_from_selection(self, _event: tk.Event) -> None:
        customer = self.table.selected_item()
        if customer is None:
            return
        self.fields["code"].set(customer.code)
        self.fields["name"].set(customer.name)
        self.fields["phone"].set(customer.phone)
        self.fields["email"].set(customer.email)
        self.fields["address"].set(customer.address)
        self.fields["password"].set(customer.password)

    def clear_form(self) -> None:
        for variable in self.fields.values():
            variable.set("")

    def _payload(self) -> dict[str, str]:
        return customer_payload({key: variable.get() for key, variable in self.fields.items()})


class RentalAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.pickup_date = tk.StringVar(value=date.today().isoformat())
        self.days = tk.StringVar(value="1")
        self.customer_choice: ChoiceBox[str]
        self.vehicle_choice: ChoiceBox[str]
        self.table: DataTable[Rental]
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Criar aluguel", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(form, text="Cliente").grid(row=0, column=0, sticky="w", pady=3)
        self.customer_choice = ChoiceBox(form, (), width=34)
        self.customer_choice.grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Veículo").grid(row=1, column=0, sticky="w", pady=3)
        self.vehicle_choice = ChoiceBox(form, (), width=34)
        self.vehicle_choice.grid(row=1, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Data de retirada").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.pickup_date).grid(row=2, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Dias").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.days).grid(row=3, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)

        ttk.Button(form, text="Criar aluguel", command=self.create_rental).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(10, 2)
        )
        ttk.Button(form, text="Finalizar aluguel selecionado", command=self.finish_selected).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=2
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
            rental = self.controller.post_rental(
                rental_payload(
                    self.customer_choice.require_value(),
                    self.vehicle_choice.require_value(),
                    self.pickup_date.get(),
                    self.days.get(),
                )
            )
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
        self.customer_choice.set_choices(customer_choices(self.controller.get_customers()))
        self.vehicle_choice.set_choices(
            available_vehicle_choices(self.controller.get_vehicles(available_vehicle_filter()))
        )
        self.table.set_items(self.controller.get_rentals())


class ReportFrame(BaseFrame):
    def refresh(self) -> None:
        pass
#     def __init__(self, parent: tk.Widget, controller: AppController) -> None:
#         super().__init__(parent, controller)
#         self.available_table: DataTable[Vehicle]
#         self.active_table: DataTable[tuple[Rental, float]]
#         self._build()
#         self.refresh()
#
#     def _build(self) -> None:
#         toolbar = ttk.Frame(self)
#         toolbar.pack(fill="x", pady=(0, 8))
#         ttk.Button(toolbar, text="Atualizar", command=self.refresh).pack(side="left", padx=(0, 6))
#         ttk.Button(toolbar, text="Exportar CSV", command=self.export_csv).pack(side="left")
#
#         panes = ttk.PanedWindow(self, orient="horizontal")
#         panes.pack(fill="both", expand=True)
#
#         available_box = ttk.LabelFrame(panes, text="Veículos disponíveis", padding=8)
#         active_box = ttk.LabelFrame(panes, text="Aluguéis ativos", padding=8)
#         panes.add(available_box, weight=1)
#         panes.add(active_box, weight=1)
#
#         self.available_table = DataTable(
#             available_box,
#             (
#                 Column("plate", "Placa", 110),
#                 Column("brand", "Marca", 110),
#                 Column("model", "Modelo", 110),
#                 Column("type", "Tipo", 110),
#                 Column("rate", "Diária", 110),
#             ),
#             report_vehicle_row,
#         )
#         self.available_table.pack(fill="both", expand=True)
#
#         self.active_table = DataTable(
#             active_box,
#             (
#                 Column("id", "ID", 110),
#                 Column("customer", "Cliente", 110),
#                 Column("vehicle", "Veículo", 110),
#                 Column("return", "Devolução prevista", 110),
#                 Column("total", "Total", 110),
#                 Column("late_fee", "Multa", 110),
#             ),
#             report_rental_row,
#         )
#         self.active_table.pack(fill="both", expand=True)
#
#     def refresh(self) -> None:
#         self.available_table.set_items(self.controller.get_vehicles(available_vehicle_filter()))
#         self.active_table.set_items(self._active_rentals_with_fees())
#
#     def export_csv(self) -> None:
#         default_path = Path(".data") / "rental_report.csv"
#         file_path = filedialog.asksaveasfilename(
#             title="Exportar relatório",
#             initialfile=default_path.name,
#             defaultextension=".csv",
#             filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")),
#         )
#         if not file_path:
#             return
#         try:
#             vehicles = self.controller.get_vehicles(available_vehicle_filter())
#             active_rentals = self._active_rentals_with_fees()
#             with open(file_path, "w", newline="", encoding="utf-8") as file:
#                 csv.writer(file).writerows(report_csv_rows(vehicles, active_rentals))
#             self.show_success(f"Relatório exportado para {file_path}.")
#         except Exception as error:
#             self.show_error(error)
#
#     def _active_rentals_with_fees(self) -> tuple[tuple[Rental, float], ...]:
#         return tuple(
#             (rental, self.controller.get_rental_late_fee(rental.rental_id or 0))
#             for rental in self.controller.get_rentals(active_rental_filter())
#         )
