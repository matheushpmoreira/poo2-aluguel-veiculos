import tkinter as tk
from tkinter import ttk

from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController
from matheushpmoreira.vehicle_rental_system.frontend.admin.customers import CustomerAdminFrame
from matheushpmoreira.vehicle_rental_system.frontend.admin.rentals import RentalAdminFrame
# from matheushpmoreira.vehicle_rental_system.frontend.admin.vehicles import VehicleAdminFrame
from matheushpmoreira.vehicle_rental_system.frontend.base import BaseFrame


class AdminPanel(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)

        header = ttk.Label(self, text="Operações administrativas", style="Title.TLabel")
        header.pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        # notebook.add(VehicleAdminFrame(notebook, controller), text="Veículos")
        notebook.add(CustomerAdminFrame(notebook, controller), text="Clientes")
        notebook.add(RentalAdminFrame(notebook, controller), text="Aluguéis")
        notebook.add(ReportFrame(notebook, controller), text="Relatórios")


class ReportFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        ttk.Label(self, text="Relatórios", style="Title.TLabel").pack(anchor="w")

    def refresh(self) -> None:
        pass
