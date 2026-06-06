from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from system.backend.controllers import AppController

from .admin import AdminPanel
from .public import PublicPanel


class RentalSystemApp(tk.Tk):
    def __init__(self, controller: AppController) -> None:
        super().__init__()
        self.controller = controller

        # Propriedades da janela
        self.title("Sistema de Aluguel de Veículos")
        self.wm_attributes("-type", "dialog")

        # Dimensões e centralização da janela
        x, y = 1280, 720
        self.minsize(960, 540)
        self.geometry(f"{x}x{y}+{(self.winfo_screenwidth() - x) // 4}+{(self.winfo_screenheight() - y) // 2}")

        # Estilização
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=(10, 6))
        style.configure("Treeview", rowheight=26)
        style.configure("Title.TLabel", font=("TkDefaultFont", 14, "bold"))

        # Layout
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        notebook.add(AdminPanel(notebook, self.controller), text="Painel Administrativo")
        notebook.add(PublicPanel(notebook, self.controller), text="Painel Público")
