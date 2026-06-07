import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable, Iterable

from matheushpmoreira.vehicle_rental_system.frontend.choices import Option


@dataclass(frozen=True)
class TextFieldSpec:
    key: str
    label: str
    default: str = ""
    width: int | None = None
    show: str = ""


@dataclass(frozen=True)
class ChoiceFieldSpec:
    key: str
    label: str
    choices: Iterable[Option]
    width: int | None = None


class TextInput:
    def __init__(self, parent: tk.Widget, spec: TextFieldSpec) -> None:
        self.key = spec.key
        self.label = ttk.Label(parent, text=spec.label)
        self.variable = tk.StringVar(value=spec.default)
        entry_options: dict[str, object] = {"textvariable": self.variable}
        if spec.width is not None:
            entry_options["width"] = spec.width
        if spec.show:
            entry_options["show"] = spec.show
        self.entry = ttk.Entry(parent, **entry_options)

    def grid(self, row: int) -> None:
        self.label.grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))
        self.entry.grid(row=row, column=1, sticky="ew", pady=3)

    def get_value(self) -> str:
        return self.variable.get()

    def set_value(self, value: object) -> None:
        self.variable.set(str(value))

    def clear(self) -> None:
        self.variable.set("")


class SelectInput:
    def __init__(self, parent: tk.Widget, spec: ChoiceFieldSpec) -> None:
        self.key = spec.key
        self.label = ttk.Label(parent, text=spec.label)
        self.variable = tk.StringVar()
        combobox_options: dict[str, object] = {"textvariable": self.variable, "state": "readonly"}
        if spec.width is not None:
            combobox_options["width"] = spec.width
        self.combobox = ttk.Combobox(parent, **combobox_options)
        self.options: tuple[Option, ...] = ()
        self.set_options(spec.choices)

    def grid(self, row: int) -> None:
        self.label.grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))
        self.combobox.grid(row=row, column=1, sticky="ew", pady=3)

    def pack(self, **kwargs: object) -> None:
        self.combobox.pack(**kwargs)

    def get_value(self) -> str:
        index = self.combobox.current()
        if 0 <= index < len(self.options):
            return self.options[index].value
        return ""

    def require_value(self) -> str:
        value = self.get_value()
        if not value:
            raise ValueError("Nenhuma opção foi selecionada.")
        return value

    def set_options(self, options: Iterable[Option]) -> None:
        current_value = self.get_value()
        self.options = tuple(options)
        self.combobox["values"] = tuple(option.label for option in self.options)
        if current_value and self.set_value(current_value):
            return
        self.clear()

    def set_value(self, value: str) -> bool:
        for index, option in enumerate(self.options):
            if option.value == value:
                self.combobox.current(index)
                return True
        return False

    def clear(self) -> None:
        if self.options:
            self.combobox.current(0)
        else:
            self.variable.set("")


FieldSpec = TextFieldSpec | ChoiceFieldSpec


class FormFrame(ttk.LabelFrame):
    def __init__(self, parent: tk.Widget, title: str, fields: Iterable[FieldSpec]) -> None:
        super().__init__(parent, text=title, padding=10)
        self._text_inputs: dict[str, TextInput] = {}
        self._choice_inputs: dict[str, SelectInput] = {}
        self._next_row = 0

        for field in fields:
            if isinstance(field, TextFieldSpec):
                input_widget = TextInput(self, field)
                self._text_inputs[field.key] = input_widget
            else:
                input_widget = SelectInput(self, field)
                self._choice_inputs[field.key] = input_widget
            input_widget.grid(self._next_row)
            self._next_row += 1

        self.columnconfigure(1, weight=1)

    def add_action_buttons(self, actions: Iterable[tuple[str, Callable[[], None]]]) -> None:
        buttons = ttk.Frame(self)
        buttons.grid(row=self._next_row, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for label, command in actions:
            ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2)
        self._next_row += 1

    def text_value(self, key: str) -> str:
        return self._text_inputs[key].get_value()

    def text_values(self) -> dict[str, str]:
        return {key: field.get_value() for key, field in self._text_inputs.items()}

    def set_text_values(self, values: dict[str, object]) -> None:
        for key, value in values.items():
            if key in self._text_inputs:
                self._text_inputs[key].set_value(value)

    def choice_value(self, key: str) -> str:
        return self._choice_inputs[key].get_value()

    def require_choice(self, key: str) -> str:
        return self._choice_inputs[key].require_value()

    def set_choice_options(self, key: str, options: Iterable[Option]) -> None:
        self._choice_inputs[key].set_options(options)

    def select_choice(self, key: str, value: str) -> bool:
        return self._choice_inputs[key].set_value(value)

    def clear(self) -> None:
        for field in self._text_inputs.values():
            field.clear()
        for field in self._choice_inputs.values():
            field.clear()
