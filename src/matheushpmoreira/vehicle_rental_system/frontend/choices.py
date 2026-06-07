
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Generic, Iterable, TypeVar

from matheushpmoreira.vehicle_rental_system.backend.models import VehicleStatus, VehicleType

from matheushpmoreira.vehicle_rental_system.frontend.labels import vehicle_status_label, vehicle_type_label

T = TypeVar("T")


@dataclass(frozen=True)
class Choice(Generic[T]):
    value: T
    label: str


class PairCombobox(ttk.Combobox):
    def __init__(self, master=None, *, values: dict[str, str], **kw):
        super().__init__(master, values=tuple(values.keys()), **kw)
        self.values = values

    def selection_get(self, **kw) -> str:
        sel = super().selection_get(**kw)
        return self.values[sel]


class ChoiceBox(Generic[T]):
    def __init__(self, parent: tk.Widget, choices: Iterable[Choice[T]], width: int | None = None) -> None:
        self.variable = tk.StringVar()
        self.widget = ttk.Combobox(parent, textvariable=self.variable, state="readonly", width=width)
        self.choices: tuple[Choice[T], ...] = ()
        self.set_choices(tuple(choices))

    def grid(self, **kwargs: object) -> None:
        self.widget.grid(**kwargs)

    def pack(self, **kwargs: object) -> None:
        self.widget.pack(**kwargs)

    def set_choices(self, choices: Iterable[Choice[T]]) -> None:
        current_value = self.selected_value(default=None)
        self.choices = tuple(choices)
        self.widget["values"] = tuple(choice.label for choice in self.choices)
        if current_value is not None and self.select_value(current_value):
            return
        if self.choices:
            self.widget.current(0)
        else:
            self.variable.set("")

    def selected_value(self, default: T | None = None) -> T | None:
        index = self.widget.current()
        if 0 <= index < len(self.choices):
            return self.choices[index].value
        return default

    def require_value(self) -> T:
        value = self.selected_value()
        if value is None:
            raise ValueError("Nenhuma opção foi selecionada.")
        return value

    def select_first(self) -> None:
        if self.choices:
            self.widget.current(0)
        else:
            self.variable.set("")

    def select_value(self, value: T) -> bool:
        for index, choice in enumerate(self.choices):
            if choice.value == value:
                self.widget.current(index)
                return True
        return False


def vehicle_type_choices() -> tuple[Choice[VehicleType], ...]:
    return tuple(Choice(vehicle_type, vehicle_type_label(vehicle_type)) for vehicle_type in VehicleType)


def vehicle_status_choices() -> tuple[Choice[VehicleStatus], ...]:
    return tuple(Choice(status, vehicle_status_label(status)) for status in VehicleStatus)


def vehicle_status_filter_choices() -> tuple[Choice[VehicleStatus | None], ...]:
    return Choice(None, ""), *vehicle_status_choices()
