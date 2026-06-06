import tkinter as tk
from collections.abc import Sequence
from tkinter import ttk

from system.backend.controllers import AppController
from system.frontend.choices import vehicle_type_choices, ChoiceBox, Choice, vehicle_status_choices


class Form:
    pass


class VehicleForm(ttk.LabelFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, text="Cadastro de veículos", padding=10)
        self.pack(side="left", fill="y", padx=(0, 10))
        self.fields: dict[str, tk.StringVar] = {
            field: tk.StringVar() for field in ("plate", "brand", "model", "year", "daily_rate")
        }

        self._input("Placa", "plate", 0)
        self._input("Marca", "brand", 1)
        self._input("Modelo", "model", 2)
        self._input("Ano", "year", 3)
        self._choice("Tipo", vehicle_type_choices(), 4)
        self._input("Valor da diária", "daily_rate", 5)
        self._choice("Situação", vehicle_status_choices(), 6)


    def _input(self, label: str, key: str, row: int) -> None:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(self, textvariable=self.fields[key]).grid(row=row, column=1, sticky="ew", pady=3)


    def _choice(self, label: str, choices: Sequence[Choice], row: int) -> None:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ChoiceBox(self, choices).grid(row=row, column=1, sticky="ew", pady=3)

    def payload(self) -> dict[str, str]:
        # return {key: value.get() for key, value in self.fields.items()} |
        pass
