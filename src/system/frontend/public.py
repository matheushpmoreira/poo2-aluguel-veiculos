
import tkinter as tk
from datetime import date
from tkinter import ttk

from system.backend.controllers import AppController
from system.backend.models import Customer, Rental, Vehicle

from .base import BaseFrame
from .formatters import available_vehicle_filter, public_rental_row, public_vehicle_row, rental_payload
from .tables import Column, DataTable


class PublicPanel(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.customer: Customer | None = None
        self.code = tk.StringVar()
        self.password = tk.StringVar()
        self.pickup_date = tk.StringVar(value=date.today().isoformat())
        self.days = tk.StringVar(value="1")
        self.status_text = tk.StringVar(value="Não autenticado")
        self.available_table: DataTable[Vehicle]
        self.rental_table: DataTable[Rental]
        self._build()
        self.refresh_public_lists()

    def _build(self) -> None:
        login_box = ttk.LabelFrame(self, text="Acesso do cliente", padding=10)
        login_box.pack(fill="x", pady=(0, 8))
        ttk.Label(login_box, text="Código ou CPF").pack(side="left", padx=(0, 6))
        ttk.Entry(login_box, textvariable=self.code, width=18).pack(side="left", padx=(0, 8))
        ttk.Label(login_box, text="Senha").pack(side="left", padx=(0, 6))
        ttk.Entry(login_box, textvariable=self.password, show="*", width=18).pack(side="left", padx=(0, 8))
        ttk.Button(login_box, text="Entrar", command=self.login).pack(side="left", padx=(0, 6))
        ttk.Button(login_box, text="Sair", command=self.logout).pack(side="left", padx=(0, 12))
        ttk.Label(login_box, textvariable=self.status_text).pack(side="left")

        rental_box = ttk.LabelFrame(self, text="Alugar veículo", padding=10)
        rental_box.pack(fill="x", pady=(0, 8))
        ttk.Label(rental_box, text="Data de retirada").pack(side="left", padx=(0, 6))
        ttk.Entry(rental_box, textvariable=self.pickup_date, width=14).pack(side="left", padx=(0, 8))
        ttk.Label(rental_box, text="Dias").pack(side="left", padx=(0, 6))
        ttk.Entry(rental_box, textvariable=self.days, width=8).pack(side="left", padx=(0, 8))
        ttk.Button(rental_box, text="Alugar veículo selecionado", command=self.create_customer_rental).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(rental_box, text="Atualizar", command=self.refresh_public_lists).pack(side="left")

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)
        available_box = ttk.LabelFrame(panes, text="Veículos disponíveis", padding=8)
        rentals_box = ttk.LabelFrame(panes, text="Meus aluguéis", padding=8)
        panes.add(available_box, weight=1)
        panes.add(rentals_box, weight=1)

        self.available_table = DataTable(
            available_box,
            (
                Column("plate", "Placa"),
                Column("brand", "Marca"),
                Column("model", "Modelo"),
                Column("year", "Ano"),
                Column("type", "Tipo"),
                Column("rate", "Diária"),
            ),
            public_vehicle_row,
        )
        self.available_table.pack(fill="both", expand=True)

        self.rental_table = DataTable(
            rentals_box,
            (
                Column("id", "ID"),
                Column("vehicle", "Veículo"),
                Column("pickup", "Retirada"),
                Column("return", "Devolução prevista"),
                Column("days", "Dias"),
                Column("total", "Total"),
                Column("status", "Situação"),
            ),
            public_rental_row,
        )
        self.rental_table.pack(fill="both", expand=True)

    def login(self) -> None:
        try:
            self.customer = self.controller.post_customer_login({"code": self.code.get(), "password": self.password.get()})
            self.status_text.set(f"Autenticado como {self.customer.name}")
            self.refresh_public_lists()
        except Exception as error:
            self.customer = None
            self.status_text.set("Não autenticado")
            self.show_error(error)

    def logout(self) -> None:
        self.customer = None
        self.password.set("")
        self.status_text.set("Não autenticado")
        self.refresh_public_lists()

    def create_customer_rental(self) -> None:
        if self.customer is None:
            self.show_warning("Login obrigatório", "É necessário fazer login como cliente.")
            return
        vehicle = self.available_table.selected_item()
        if vehicle is None:
            self.show_warning("Seleção obrigatória", "Selecione um veículo disponível primeiro.")
            return
        try:
            rental = self.controller.post_rental(
                rental_payload(self.customer.code, vehicle.plate, self.pickup_date.get(), self.days.get())
            )
            self.show_success(f"Aluguel {rental.rental_id} criado. Total: {rental.total_amount:.2f}")
            self.refresh_public_lists()
        except Exception as error:
            self.show_error(error)

    def refresh_public_lists(self) -> None:
        self.available_table.set_items(self.controller.get_vehicles(available_vehicle_filter()))
        if self.customer is None:
            self.rental_table.clear()
            return
        self.rental_table.set_items(self.controller.get_rentals({"customer_code": self.customer.code}))
