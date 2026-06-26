import tkinter as tk
from tkinter import ttk

from clivet.controllers import AppController
from clivet.views.frames import AnimalFrame, BookingFrame, HistoryFrame, ServiceFrame, TutorFrame


class PetClinicApp(tk.Tk):
    def __init__(self, controller: AppController) -> None:
        super().__init__()
        self.controller = controller
        self.title("Clivet - Clínica Veterinária")
        self.minsize(1080, 640)
        self.geometry("1280x720")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=(10, 6))
        style.configure("Treeview", rowheight=26)
        style.configure("Title.TLabel", font=("TkDefaultFont", 14, "bold"))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tutor_frame = TutorFrame(notebook, controller)
        self.animal_frame = AnimalFrame(notebook, controller)
        self.service_frame = ServiceFrame(notebook, controller)
        self.booking_frame = BookingFrame(notebook, controller)
        self.history_frame = HistoryFrame(notebook, controller)

        notebook.add(self.tutor_frame, text="Tutores")
        notebook.add(self.animal_frame, text="Animais")
        notebook.add(self.service_frame, text="Serviços")
        notebook.add(self.booking_frame, text="Agendamentos")
        notebook.add(self.history_frame, text="Histórico")
        notebook.bind("<<NotebookTabChanged>>", self._refresh_current_tab)

    def _refresh_current_tab(self, event: tk.Event) -> None:
        selected = event.widget.nametowidget(event.widget.select())
        if hasattr(selected, "refresh"):
            selected.refresh()
