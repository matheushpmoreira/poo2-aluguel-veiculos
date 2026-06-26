import tkinter as tk
from datetime import date
from tkinter import ttk

from clivet.controllers import AppController
from clivet.models import *
from clivet.views.choices import *
from clivet.views.formatters import *
from clivet.views.widgets import *


class ServiceFrame(ViewFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller
        self.fields = {key: tk.StringVar() for key in ("code", "name", "description", "base_value", "duration")}
        self.veterinarian = tk.StringVar()
        self.specialty = tk.StringVar()
        self.nail_clipping = tk.BooleanVar()
        self.perfume = tk.BooleanVar()
        self.batch = tk.StringVar()
        self.expiration_date = tk.StringVar(value=date.today().isoformat())
        self.laboratory = tk.StringVar()
        self.daily_rate = tk.StringVar()
        self.capacity = tk.StringVar(value="1")
        self.type_choice: ChoiceBox[ServiceType]
        self.type_frames: dict[ServiceType, ttk.Frame] = {}
        self.table: DataTable[Service]
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text="Cadastro de serviços", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Serviço", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))
        for row, (key, label) in enumerate(
            (
                ("code", "Código"),
                ("name", "Nome"),
                ("description", "Descrição"),
                ("base_value", "Valor base"),
                ("duration", "Duração min."),
            )
        ):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=self.fields[key], width=28).grid(row=row, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Tipo").grid(row=5, column=0, sticky="w", pady=3)
        self.type_choice = ChoiceBox(form, service_type_choices())
        self.type_choice.grid(row=5, column=1, sticky="ew", pady=3)
        self.type_choice.bind("<<ComboboxSelected>>", lambda _event: self.show_type_fields())
        type_area = ttk.Frame(form)
        type_area.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self._build_type_frames(type_area)
        buttons = ttk.Frame(form)
        buttons.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for label, command in (
            ("Cadastrar", self.create),
            ("Atualizar", self.update),
            ("Remover", self.delete),
            ("Limpar", self.clear),
        ):
            ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2)
        form.columnconfigure(1, weight=1)

        self.table = DataTable(
            container,
            (
                Column("code", "Código", 100),
                Column("name", "Nome", 150),
                Column("type", "Tipo", 145),
                Column("value", "Valor", 90),
                Column("duration", "Min.", 70),
                Column("details", "Detalhes", 320),
            ),
            service_row,
        )
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.fill_from_selection)
        self.show_type_fields()

    def _build_type_frames(self, parent: tk.Widget) -> None:
        consultation = ttk.LabelFrame(parent, text="Consulta", padding=8)
        ttk.Label(consultation, text="Veterinário").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(consultation, textvariable=self.veterinarian).grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Label(consultation, text="Especialidade").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(consultation, textvariable=self.specialty).grid(row=1, column=1, sticky="ew", pady=3)
        self.type_frames[ServiceType.CONSULTATION] = consultation

        bath = ttk.LabelFrame(parent, text="Banho e tosa", padding=8)
        ttk.Checkbutton(bath, text="Corte de unhas", variable=self.nail_clipping).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(bath, text="Perfume", variable=self.perfume).grid(row=1, column=0, sticky="w")
        self.type_frames[ServiceType.BATH_GROOMING] = bath

        vaccination = ttk.LabelFrame(parent, text="Vacinação", padding=8)
        for row, (label, variable) in enumerate(
            (("Lote", self.batch), ("Validade", self.expiration_date), ("Laboratório", self.laboratory))
        ):
            ttk.Label(vaccination, text=label).grid(row=row, column=0, sticky="w", pady=3)
            if label == "Validade":
                DateEntry(vaccination, textvariable=variable, width=20).grid(row=row, column=1, sticky="ew", pady=3)
            else:
                ttk.Entry(vaccination, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=3)
        self.type_frames[ServiceType.VACCINATION] = vaccination

        exam = ttk.LabelFrame(parent, text="Exame", padding=8)
        ttk.Label(exam, text="Sem campos adicionais").grid(row=0, column=0, sticky="w", pady=3)
        self.type_frames[ServiceType.EXAM] = exam

        surgery = ttk.LabelFrame(parent, text="Cirurgia", padding=8)
        ttk.Label(surgery, text="Sem campos adicionais").grid(row=0, column=0, sticky="w", pady=3)
        self.type_frames[ServiceType.SURGERY] = surgery

        housing = ttk.LabelFrame(parent, text="Hospedagem", padding=8)
        ttk.Label(housing, text="Diária").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(housing, textvariable=self.daily_rate).grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Label(housing, text="Capacidade").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(housing, textvariable=self.capacity).grid(row=1, column=1, sticky="ew", pady=3)
        self.type_frames[ServiceType.HOUSING] = housing

    def show_type_fields(self) -> None:
        for frame in self.type_frames.values():
            frame.grid_forget()
        service_type = self.type_choice.require_value()
        self.type_frames[service_type].grid(row=0, column=0, sticky="ew")

    def create(self) -> None:
        try:
            self.controller.post_service(self._payload())
            self.show_success("Serviço cadastrado.")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update(self) -> None:
        try:
            self.controller.put_service(self.fields["code"].get(), self._payload())
            self.show_success("Serviço atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete(self) -> None:
        try:
            self.controller.delete_service(self.fields["code"].get())
            self.show_success("Serviço removido.")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.table.set_items(self.controller.get_services())

    def fill_from_selection(self, _event: tk.Event) -> None:
        service = self.table.selected_item()
        if service is None:
            return
        self.fields["code"].set(service.code)
        self.fields["name"].set(service.name)
        self.fields["description"].set(service.description)
        self.fields["base_value"].set(f"{service.base_value:.2f}")
        self.fields["duration"].set(str(service.duration_minutes))
        self.type_choice.select_value(service.service_type)
        if isinstance(service, Consultation):
            self.veterinarian.set(service.veterinarian)
            self.specialty.set(service.specialty)
        if isinstance(service, BathGrooming):
            self.nail_clipping.set(service.nail_clipping)
            self.perfume.set(service.perfume)
        if isinstance(service, Vaccination):
            self.batch.set(service.batch)
            self.expiration_date.set(service.expiration_date.isoformat())
            self.laboratory.set(service.laboratory)
        if hasattr(service, "daily_rate"):
            self.daily_rate.set(f"{service.daily_rate:.2f}")
            self.capacity.set(str(service.accommodation_capacity))
        self.show_type_fields()

    def clear(self) -> None:
        for variable in self.fields.values():
            variable.set("")
        self.veterinarian.set("")
        self.specialty.set("")
        self.nail_clipping.set(False)
        self.perfume.set(False)
        self.batch.set("")
        self.expiration_date.set(date.today().isoformat())
        self.laboratory.set("")
        self.daily_rate.set("")
        self.capacity.set("1")
        self.type_choice.select_first()
        self.show_type_fields()

    def _payload(self) -> dict[str, object]:
        return {
            "code": self.fields["code"].get(),
            "name": self.fields["name"].get(),
            "service_type": self.type_choice.require_value().value,
            "description": self.fields["description"].get(),
            "base_value": self.fields["base_value"].get(),
            "duration_minutes": self.fields["duration"].get(),
            "veterinarian": self.veterinarian.get(),
            "specialty": self.specialty.get(),
            "nail_clipping": self.nail_clipping.get(),
            "perfume": self.perfume.get(),
            "batch": self.batch.get(),
            "expiration_date": self.expiration_date.get(),
            "laboratory": self.laboratory.get(),
            "daily_rate": self.daily_rate.get() or self.fields["base_value"].get(),
            "accommodation_capacity": self.capacity.get(),
        }
