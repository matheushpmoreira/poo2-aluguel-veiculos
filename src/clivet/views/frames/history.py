import tkinter as tk
from tkinter import ttk

from clivet.controllers import AppController
from clivet.models import *
from clivet.views.choices import *
from clivet.views.formatters import *
from clivet.views.labels import *
from clivet.views.widgets import *


class HistoryFrame(ViewFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller
        self.animal_choice: ChoiceBox[str]
        self.details = tk.StringVar()
        self.table: DataTable[Booking]
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text="Histórico do animal", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        filters = ttk.Frame(self)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Animal").pack(side="left", padx=(0, 6))
        self.animal_choice = ChoiceBox(filters, (), width=34)
        self.animal_choice.pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Consultar", command=self.load_history).pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Atualizar", command=self.refresh).pack(side="left")
        ttk.Label(self, textvariable=self.details).pack(anchor="w", pady=(0, 8))
        self.table = DataTable(
            self,
            (
                Column("code", "Código", 90),
                Column("animal", "Animal", 100),
                Column("services", "Serviços", 180),
                Column("start", "Início", 130),
                Column("end", "Término", 130),
                Column("total", "Total", 90),
                Column("status", "Status", 110),
            ),
            booking_row,
        )
        self.table.pack(fill="both", expand=True)

    def refresh(self) -> None:
        animals = self.controller.get_animals()
        self.animal_choice.set_choices(animal_choices(animals))
        if animals:
            self.load_history()

    def load_history(self) -> None:
        try:
            animal_code = self.animal_choice.require_value()
            animal = self.controller.get_animal(animal_code)
            self.details.set(
                f"{animal.name} | {species_label(animal.species)} | "
                f"{animal_status_label(animal.status)} | {animal_details(animal)}"
            )
            self.table.set_items(self.controller.get_animal_history(animal_code))
        except Exception as error:
            self.show_error(error)
