import tkinter as tk
from tkinter import messagebox, ttk

from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController


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
