import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk

from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController
from matheushpmoreira.vehicle_rental_system.frontend.lang import lang


class Input(ABC):
    @abstractmethod
    def get_value(self) -> str: ...

    @abstractmethod
    def set_value(self, value: str) -> None: ...

    @abstractmethod
    def grid(self, row: int) -> None: ...


class Field(Input):
    def __init__(self, master: tk.Widget, label: str) -> None:
        self.label = ttk.Label(master, text=label)
        self.entry = ttk.Entry(master, textvariable=tk.StringVar())

    def get_value(self) -> str:
        return self.entry.get()

    def set_value(self, value: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

    def grid(self, row: int) -> None:
        self.label.grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))
        self.entry.grid(row=row, column=1, sticky="we", pady=3)


class Choice(Input):
    def __init__(self, master: tk.Widget, label: str, values: dict[str, str]) -> None:
        self.label = ttk.Label(master, text=label)
        self.combobox = ttk.Combobox(
            master, textvariable=tk.StringVar(), state="readonly", values=tuple(values.values())
        )
        self.values = values
        self.key = ""

    def get_value(self) -> str:
        return self.key

    def set_value(self, key: str) -> None:
        self.combobox.set(self.values.get(key, ""))
        self.key = key
        # print(self.values, key)

    def grid(self, row: int) -> None:
        self.label.grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))
        self.combobox.grid(row=row, column=1, sticky="ew", pady=3)


class Form(ABC, ttk.LabelFrame):
    inputs: dict[str, Input]

    def pack(self, *args, **kwargs) -> None:
        super().pack(*args, **kwargs)
        for idx, input in enumerate(self.inputs.values()):
            input.grid(idx)


class VehicleForm(Form):
    def __init__(self, parent: tk.Widget, controller: AppController, com) -> None:
        super().__init__(parent, text="Cadastro de veículos", padding=10)

        self.inputs = {
            "plate": Field(self, lang["vehicle"]["attr"]["plate"]),
            "brand": Field(self, lang["vehicle"]["attr"]["brand"]),
            "model": Field(self, lang["vehicle"]["attr"]["model"]),
            "year": Field(self, lang["vehicle"]["attr"]["year"]),
            "type": Choice(self, lang["vehicle"]["attr"]["type"], lang["vehicle"]["type"].copy()),
            "daily_rate": Field(self, lang["vehicle"]["attr"]["daily_rate"]),
            "status": Choice(self, lang["vehicle"]["attr"]["status"], lang["vehicle"]["status"].copy()),
        }

        self.actions = (
            ttk.Button(parent, text="Cadastrar", command=com),
            # ttk.Button(parent, text="Atualizar", command=self.command),
            # ttk.Button(parent, text="Remover", command=self.command),
            # ttk.Button(parent, text="Limpar", command=self.command),
        )

    def get_values(self) -> dict[str, str]:
        return {key: var.get_value() for key, var in self.inputs.items()}

    def set_values(self, values: dict[str, str]) -> None:
        for key, val in values.items():
            if key not in self.inputs:
                continue
            self.inputs[key].set_value(val)
