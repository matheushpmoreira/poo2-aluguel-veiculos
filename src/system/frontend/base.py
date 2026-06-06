from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable

from system.backend.controllers import AppController


@dataclass(frozen=True)
class Action:
    label: str
    command: Callable[[], None]
    # _parent: tk.Widget

    # def __post_init__(self) -> None:
    #     ttk.Button(self._parent, text=self.label, command=self.command).pack(fill="x", pady=2)

    def pack_button(self, parent: tk.Widget) -> None:
        ttk.Button(parent, text=self.label, command=self.command).pack(fill="x", pady=2)


class BaseFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller

    @staticmethod
    def show_error(error: Exception) -> None:
        messagebox.showerror("Erro", str(error))

    @staticmethod
    def show_success(message: str) -> None:
        messagebox.showinfo("Sucesso", message)

    @staticmethod
    def show_warning(title: str, message: str) -> None:
        messagebox.showwarning(title, message)


# def pack_action_buttons(parent: tk.Widget, actions: tuple[Action, ...]) -> None:
#     for action in actions:
#         ttk.Button(parent, text=action.label, command=action.command).pack(fill="x", pady=2)
