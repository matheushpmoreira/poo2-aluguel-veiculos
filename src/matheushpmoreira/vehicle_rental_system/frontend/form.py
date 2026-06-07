import tkinter as tk
from abc import ABC, abstractmethod
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable, Iterable


@dataclass(frozen=True)
class Choice:
    value: str
    label: str


@dataclass(frozen=True)
class Action:
    label: str
    command: Callable[[], None]


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
    choices: Iterable[Choice]
    width: int | None = None


class Input(ABC):
    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def get_value(self) -> str: ...

    @abstractmethod
    def set_value(self, value: object) -> None: ...

    @abstractmethod
    def grid(self, row: int) -> None: ...

    @abstractmethod
    def pack(self, **kwargs: object) -> None: ...


class TextInput(Input):
    def __init__(self, parent: tk.Widget, *, label: str) -> None:
        self.label = ttk.Label(parent, text=label)
        self.entry = ttk.Entry(parent, textvariable=tk.StringVar())

    def clear(self) -> None:
        self.entry.delete(0)

    def get_value(self) -> str:
        return self.entry.get()

    def set_value(self, value: str) -> None:
        self.clear()
        self.entry.insert(0, value)

    def grid(self, row: int) -> None:
        self.label.grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))
        self.entry.grid(row=row, column=1, sticky="ew", pady=3)

    def pack(self, **kwargs: object) -> None:
        self.entry.pack(**kwargs)


class SelectInput(Input):
    def __init__(self, parent: tk.Widget, *, label: str, choices: Iterable[Choice]) -> None:
        self.choices = {c.label: c.value for c in choices}
        self.label = ttk.Label(parent, text=label)
        self.box = ttk.Combobox(
            parent,
            textvariable=tk.StringVar(),
            state="readonly",
            values=tuple(self.choices.values()),
        )

    def get_value(self) -> str:
        return self.choices.get(self.box.get(), "")

    def set_value(self, value: str) -> None:
        self.box.set(self.choices.get(value, ""))

    def clear(self) -> None:
        self.box.set("")

    def grid(self, row: int) -> None:
        self.label.grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))
        self.box.grid(row=row, column=1, sticky="ew", pady=3)

    def pack(self, **kwargs: object) -> None:
        self.box.pack(**kwargs)


class FormFrame(ttk.LabelFrame):
    def __init__(self, parent: tk.Widget, *, title: str, inputs: dict[str, Input], buttons: Iterable[ttk.Button]) -> None:
        super().__init__(parent, text=title, padding=10)
        self.inputs = inputs
        self.buttons = buttons
        # self._next_row = 0

        for row, input in enumerate(inputs.values()):
            # if isinstance(field, TextFieldSpec):
            #     input_widget = TextInput(self, field)
            # else:
            #     input_widget = SelectInput(self, field)
            # self.inputs[field.key] = input_widget
            input.grid(row)
            # self._next_row += 1

        for row, button in enumerate(buttons, start=len(inputs)):
            button.grid(row=row, column=0, sticky="ew", pady=2)

    # def add_action_buttons(self, actions: Iterable[tuple[str, Callable[[], None]]]) -> None:
    #     buttons = ttk.Frame(self)
    #     buttons.grid(row=self._next_row, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    #     for label, command in actions:
    #         ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2)
    #     self._next_row += 1

    def input_value(self, key: str) -> str:
        return self.inputs[key].get_value()

    def get_values(self) -> dict[str, str]:
        return {key: field.get_value() for key, field in self.inputs.items()}

    def set_values(self, values: dict[str, str]) -> None:
        for key, value in values.items():
            if key in self.inputs:
                self.inputs[key].set_value(value)

    # def set_choice_options(self, key: str, options: Iterable[Choice]) -> None:
    #     input_widget = self.inputs[key]
    #     if isinstance(input_widget, SelectInput):
    #         input_widget.set_options(options)

    # def set_input_value(self, key: str, value: object) -> None:
    #     self.inputs[key].set_value(value)

    def clear(self) -> None:
        for input in self.inputs.values():
            input.clear()

    def pack(self, **kwargs: object) -> None:
        super().pack(**kwargs)

        for row, input in enumerate(self.inputs.values()):
            input.grid(row)

        for row, button in enumerate(self.buttons, start=len(self.inputs)):
            button.grid(row=row, column=0, sticky="ew", pady=2)

        self.columnconfigure(1, weight=1)
