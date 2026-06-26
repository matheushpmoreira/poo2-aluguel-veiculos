import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk

from clivet.controllers import AppController
from clivet.models import *
from clivet.views.choices import *
from clivet.views.formatters import *
from clivet.views.labels import *
from clivet.views.widgets import *

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


class TutorFrame(ViewFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller
        self.fields = {key: tk.StringVar() for key in ("cpf", "name", "phone", "email", "address")}
        self.table: DataTable[Tutor]
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text="Cadastro de tutores", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Tutor", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))
        for row, (key, label) in enumerate(
            (
                ("cpf", "CPF"),
                ("name", "Nome completo"),
                ("phone", "Telefone"),
                ("email", "E-mail"),
                ("address", "Endereço"),
            )
        ):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=self.fields[key], width=28).grid(row=row, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)
        buttons = ttk.Frame(form)
        buttons.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for label, command in (
            ("Cadastrar", self.create),
            ("Atualizar", self.update),
            ("Remover", self.delete),
            ("Limpar", self.clear),
        ):
            ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2)

        self.table = DataTable(
            container,
            (
                Column("cpf", "CPF", 130),
                Column("name", "Nome", 180),
                Column("phone", "Telefone", 120),
                Column("email", "E-mail", 190),
                Column("address", "Endereço", 260),
            ),
            lambda tutor: (tutor.cpf, tutor.name, tutor.phone, tutor.email, tutor.address),
        )
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.fill_from_selection)

    def create(self) -> None:
        try:
            self.controller.post_tutor(self._payload())
            self.show_success("Tutor cadastrado.")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update(self) -> None:
        try:
            self.controller.put_tutor(self.fields["cpf"].get(), self._payload())
            self.show_success("Tutor atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete(self) -> None:
        try:
            self.controller.delete_tutor(self.fields["cpf"].get())
            self.show_success("Tutor removido.")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.table.set_items(self.controller.get_tutors())

    def fill_from_selection(self, _event: tk.Event) -> None:
        tutor = self.table.selected_item()
        if tutor is None:
            return
        self.fields["cpf"].set(tutor.cpf)
        self.fields["name"].set(tutor.name)
        self.fields["phone"].set(tutor.phone)
        self.fields["email"].set(tutor.email)
        self.fields["address"].set(tutor.address)

    def clear(self) -> None:
        for variable in self.fields.values():
            variable.set("")

    def _payload(self) -> dict[str, str]:
        return {key: variable.get() for key, variable in self.fields.items()}


class AnimalFrame(ViewFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller
        self.fields = {key: tk.StringVar() for key in ("code", "name", "breed", "birthday", "weight")}
        self.fields["birthday"].set(date.today().isoformat())
        self.dog_rabies = tk.BooleanVar()
        self.cat_neutered = tk.BooleanVar()
        self.bird_exotic = tk.BooleanVar()
        self.bird_leg_band = tk.StringVar()
        self.species_choice: ChoiceBox[Species]
        self.status_choice: ChoiceBox[AnimalStatus]
        self.tutor_choice: ChoiceBox[str]
        self.filter_tutor_choice: ChoiceBox[str]
        self.dog_size_choice: ChoiceBox
        self.cat_hair_choice: ChoiceBox
        self.species_frames: dict[Species, ttk.Frame] = {}
        self.table: DataTable[Animal]
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text="Cadastro de animais", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Animal", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))
        for row, (key, label) in enumerate(
            (
                ("code", "Código/microchip"),
                ("name", "Nome"),
                ("breed", "Raça"),
                ("birthday", "Nascimento"),
                ("weight", "Peso"),
            )
        ):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            if key == "birthday":
                DateEntry(form, textvariable=self.fields[key], width=20).grid(row=row, column=1, sticky="ew", pady=3)
            else:
                ttk.Entry(form, textvariable=self.fields[key], width=28).grid(row=row, column=1, sticky="ew", pady=3)

        ttk.Label(form, text="Tutor").grid(row=5, column=0, sticky="w", pady=3)
        self.tutor_choice = ChoiceBox(form, ())
        self.tutor_choice.grid(row=5, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Espécie").grid(row=6, column=0, sticky="w", pady=3)
        self.species_choice = ChoiceBox(form, species_choices())
        self.species_choice.grid(row=6, column=1, sticky="ew", pady=3)
        self.species_choice.bind("<<ComboboxSelected>>", lambda _event: self.show_species_fields())
        ttk.Label(form, text="Status").grid(row=7, column=0, sticky="w", pady=3)
        self.status_choice = ChoiceBox(form, animal_status_choices())
        self.status_choice.grid(row=7, column=1, sticky="ew", pady=3)

        species_area = ttk.Frame(form)
        species_area.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self._build_species_frames(species_area)
        buttons = ttk.Frame(form)
        buttons.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for label, command in (
            ("Cadastrar", self.create),
            ("Atualizar", self.update),
            ("Remover", self.delete),
            ("Limpar", self.clear),
        ):
            ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2)
        form.columnconfigure(1, weight=1)

        list_area = ttk.Frame(container)
        list_area.pack(side="left", fill="both", expand=True)
        filters = ttk.Frame(list_area)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Tutor").pack(side="left", padx=(0, 6))
        self.filter_tutor_choice = ChoiceBox(filters, (), width=34)
        self.filter_tutor_choice.pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Filtrar", command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Limpar filtro", command=self.clear_filter).pack(side="left")

        self.table = DataTable(
            list_area,
            (
                Column("code", "Código", 110),
                Column("name", "Nome", 130),
                Column("species", "Espécie", 100),
                Column("breed", "Raça", 130),
                Column("birthday", "Nascimento", 105),
                Column("weight", "Peso", 70),
                Column("tutor", "Tutor", 130),
                Column("status", "Status", 90),
            ),
            animal_row,
        )
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.fill_from_selection)
        self.show_species_fields()

    def _build_species_frames(self, parent: tk.Widget) -> None:
        dog = ttk.LabelFrame(parent, text="Cachorro", padding=8)
        ttk.Label(dog, text="Porte").grid(row=0, column=0, sticky="w", pady=3)
        self.dog_size_choice = ChoiceBox(dog, dog_size_choices())
        self.dog_size_choice.grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Checkbutton(dog, text="Vacinado contra raiva", variable=self.dog_rabies).grid(
            row=1, column=0, columnspan=2, sticky="w"
        )
        self.species_frames[Species.DOG] = dog

        cat = ttk.LabelFrame(parent, text="Gato", padding=8)
        ttk.Checkbutton(cat, text="Castrado", variable=self.cat_neutered).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(cat, text="Pelo").grid(row=1, column=0, sticky="w", pady=3)
        self.cat_hair_choice = ChoiceBox(cat, cat_hair_choices())
        self.cat_hair_choice.grid(row=1, column=1, sticky="ew", pady=3)
        self.species_frames[Species.CAT] = cat

        bird = ttk.LabelFrame(parent, text="Ave", padding=8)
        ttk.Label(bird, text="Anilha").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(bird, textvariable=self.bird_leg_band).grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Checkbutton(bird, text="Espécie exótica", variable=self.bird_exotic).grid(
            row=1, column=0, columnspan=2, sticky="w"
        )
        self.species_frames[Species.BIRD] = bird

    def show_species_fields(self) -> None:
        for frame in self.species_frames.values():
            frame.grid_forget()
        species = self.species_choice.require_value()
        self.species_frames[species].grid(row=0, column=0, sticky="ew")

    def create(self) -> None:
        try:
            self.controller.post_animal(self._payload())
            self.show_success("Animal cadastrado.")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update(self) -> None:
        try:
            self.controller.put_animal(self.fields["code"].get(), self._payload())
            self.show_success("Animal atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete(self) -> None:
        try:
            self.controller.delete_animal(self.fields["code"].get())
            self.show_success("Animal removido.")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        tutors = self.controller.get_tutors()
        self.tutor_choice.set_choices(tutor_choices(tutors))
        self.filter_tutor_choice.set_choices(tutor_choices(tutors, include_empty=True))
        self.table.set_items(self.controller.get_animals({"tutor_cpf": self.filter_tutor_choice.selected_value("")}))

    def clear_filter(self) -> None:
        self.filter_tutor_choice.select_value("")
        self.refresh()

    def fill_from_selection(self, _event: tk.Event) -> None:
        animal = self.table.selected_item()
        if animal is None:
            return
        self.fields["code"].set(animal.code)
        self.fields["name"].set(animal.name)
        self.fields["breed"].set(animal.breed)
        self.fields["birthday"].set(animal.birthday.isoformat())
        self.fields["weight"].set(f"{animal.weight:.2f}")
        self.tutor_choice.select_value(animal.tutor_cpf)
        self.species_choice.select_value(animal.species)
        self.status_choice.select_value(animal.status)
        if isinstance(animal, Dog):
            self.dog_size_choice.select_value(animal.size)
            self.dog_rabies.set(animal.rabies_vaccinated)
        if isinstance(animal, Cat):
            self.cat_neutered.set(animal.neutered)
            self.cat_hair_choice.select_value(animal.hair_type)
        if isinstance(animal, Bird):
            self.bird_leg_band.set(animal.leg_band)
            self.bird_exotic.set(animal.exotic)
        self.show_species_fields()

    def clear(self) -> None:
        for variable in self.fields.values():
            variable.set("")
        self.fields["birthday"].set(date.today().isoformat())
        self.species_choice.select_first()
        self.status_choice.select_value(AnimalStatus.ACTIVE)
        self.dog_rabies.set(False)
        self.cat_neutered.set(False)
        self.bird_exotic.set(False)
        self.bird_leg_band.set("")
        self.show_species_fields()

    def _payload(self) -> dict[str, object]:
        return {
            "code": self.fields["code"].get(),
            "name": self.fields["name"].get(),
            "species": self.species_choice.require_value().value,
            "breed": self.fields["breed"].get(),
            "birthday": self.fields["birthday"].get(),
            "weight": self.fields["weight"].get(),
            "tutor_cpf": self.tutor_choice.require_value(),
            "status": self.status_choice.require_value().value,
            "dog_size": self.dog_size_choice.require_value().value,
            "rabies_vaccinated": self.dog_rabies.get(),
            "cat_neutered": self.cat_neutered.get(),
            "cat_hair_type": self.cat_hair_choice.require_value().value,
            "bird_leg_band": self.bird_leg_band.get(),
            "bird_exotic": self.bird_exotic.get(),
        }


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


class BookingFrame(ViewFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller
        self.code = tk.StringVar()
        self.date_text = tk.StringVar(value=date.today().isoformat())
        self.time_text = tk.StringVar(value="09:00")
        self.observations = tk.StringVar()
        self.preview = tk.StringVar(value="Término: - | Total: -")
        self.filter_date = tk.StringVar()
        self.animal_choice: ChoiceBox[str]
        self.filter_animal_choice: ChoiceBox[str]
        self.filter_status_choice: ChoiceBox
        self.status_choice: ChoiceBox
        self.service_table: DataTable[Service]
        self.booking_table: DataTable[Booking]
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text="Agendamentos", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Novo agendamento", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))
        for row, (label, variable) in enumerate(
            (
                ("Código", self.code),
                ("Data", self.date_text),
                ("Hora", self.time_text),
                ("Observações", self.observations),
            )
        ):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            if label == "Data":
                DateEntry(form, textvariable=variable, width=20).grid(row=row, column=1, sticky="ew", pady=3)
            else:
                ttk.Entry(form, textvariable=variable, width=30).grid(row=row, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Animal").grid(row=4, column=0, sticky="w", pady=3)
        self.animal_choice = ChoiceBox(form, (), width=30)
        self.animal_choice.grid(row=4, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Status").grid(row=5, column=0, sticky="w", pady=3)
        self.status_choice = ChoiceBox(form, booking_status_choices())
        self.status_choice.grid(row=5, column=1, sticky="ew", pady=3)
        ttk.Label(form, textvariable=self.preview).grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 3))
        ttk.Label(form, text="Serviços").grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 3))
        self.service_table = DataTable(
            form,
            (
                Column("code", "Código", 80),
                Column("name", "Nome", 135),
                Column("type", "Tipo", 130),
                Column("value", "Valor", 85),
                Column("duration", "Min.", 55),
            ),
            lambda service: (
                service.code,
                service.name,
                service_type_label(service.service_type),
                money(service.base_value),
                service.duration_minutes,
            ),
            selectmode="extended",
        )
        self.service_table.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(0, 6))
        self.service_table.bind("<<TreeviewSelect>>", lambda _event: self.update_preview())
        form.rowconfigure(8, weight=1)
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(form)
        buttons.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for label, command in (
            ("Calcular", self.update_preview),
            ("Cadastrar", self.create),
            ("Atualizar", self.update),
            ("Concluir", self.complete),
            ("Cancelar", self.cancel),
            ("Faltou", self.mark_missed),
            ("Remover", self.delete),
            ("Limpar", self.clear),
        ):
            ttk.Button(buttons, text=label, command=command).pack(fill="x", pady=2)

        list_area = ttk.Frame(container)
        list_area.pack(side="left", fill="both", expand=True)
        filters = ttk.Frame(list_area)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Data").pack(side="left", padx=(0, 6))
        DateEntry(filters, textvariable=self.filter_date, width=12).pack(side="left", padx=(0, 6))
        ttk.Label(filters, text="Animal").pack(side="left", padx=(0, 6))
        self.filter_animal_choice = ChoiceBox(filters, (), width=26)
        self.filter_animal_choice.pack(side="left", padx=(0, 6))
        ttk.Label(filters, text="Status").pack(side="left", padx=(0, 6))
        self.filter_status_choice = ChoiceBox(filters, booking_status_choices(include_empty=True), width=16)
        self.filter_status_choice.pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Filtrar", command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Limpar", command=self.clear_filters).pack(side="left")
        self.booking_table = DataTable(
            list_area,
            (
                Column("code", "Código", 90),
                Column("animal", "Animal", 100),
                Column("services", "Serviços", 180),
                Column("start", "Início", 130),
                Column("end", "Término", 130),
                Column("total", "Total", 90),
                Column("status", "Status", 110),
            ),
            booking_row,
        )
        self.booking_table.pack(fill="both", expand=True)
        self.booking_table.bind("<<TreeviewSelect>>", self.fill_from_selection)

    def create(self) -> None:
        try:
            booking = self.controller.post_booking(self._payload(include_status=False))
            self.show_success(f"Agendamento {booking.code} cadastrado. Total: {money(booking.total_value)}")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update(self) -> None:
        try:
            self.controller.put_booking(self.code.get(), self._payload(include_status=True))
            self.show_success("Agendamento atualizado.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def complete(self) -> None:
        self._status_action(self.controller.complete_booking, "Agendamento concluído.")

    def cancel(self) -> None:
        self._status_action(self.controller.cancel_booking, "Agendamento cancelado.")

    def mark_missed(self) -> None:
        self._status_action(self.controller.mark_booking_missed, "Falta registrada.")

    def delete(self) -> None:
        try:
            self.controller.delete_booking(self.code.get())
            self.show_success("Agendamento removido.")
            self.clear()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def _status_action(self, action, message: str) -> None:
        code = self._selected_code()
        if not code:
            self.show_warning("Seleção obrigatória", "Selecione um agendamento primeiro.")
            return
        try:
            action(code)
            self.show_success(message)
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        animals = self.controller.get_animals()
        services = self.controller.get_services()
        self.animal_choice.set_choices(animal_choices(animals))
        self.filter_animal_choice.set_choices(animal_choices(animals, include_empty=True))
        self.service_table.set_items(services)
        query = {
            "date": self.filter_date.get(),
            "animal_code": self.filter_animal_choice.selected_value(""),
            "status": self.filter_status_choice.selected_value(None),
        }
        self.booking_table.set_items(self.controller.get_bookings(query))
        self.update_preview()

    def clear_filters(self) -> None:
        self.filter_date.set("")
        self.filter_animal_choice.select_value("")
        self.filter_status_choice.select_value(None)
        self.refresh()

    def fill_from_selection(self, _event: tk.Event) -> None:
        booking = self.booking_table.selected_item()
        if booking is None:
            return
        self.code.set(booking.code)
        self.date_text.set(booking.start_at.date().isoformat())
        self.time_text.set(booking.start_at.strftime("%H:%M"))
        self.observations.set(booking.observations)
        self.animal_choice.select_value(booking.animal_code)
        self.status_choice.select_value(booking.status)
        self.service_table.select_where(lambda service: service.code in set(booking.service_codes))
        self.update_preview()

    def clear(self) -> None:
        self.code.set("")
        self.date_text.set(date.today().isoformat())
        self.time_text.set("09:00")
        self.observations.set("")
        self.status_choice.select_first()
        self.service_table.select_where(lambda _service: False)
        self.update_preview()

    def update_preview(self) -> None:
        services = self.service_table.selected_items()
        if not services:
            self.preview.set("Término: - | Total: -")
            return
        try:
            start = self._start_at()
            end = start + timedelta(minutes=sum(service.duration_minutes for service in services))
            total = sum(service.base_value for service in services)
            if start.weekday() >= 5:
                total *= 1.2
            self.preview.set(f"Término: {end.strftime('%Y-%m-%d %H:%M')} | Total: {money(round(total, 2))}")
        except ValueError:
            self.preview.set("Término: data inválida | Total: -")

    def _payload(self, include_status: bool) -> dict[str, object]:
        payload = {
            "code": self.code.get(),
            "animal_code": self.animal_choice.require_value(),
            "service_codes": [service.code for service in self.service_table.selected_items()],
            "start_at": self._start_at().isoformat(timespec="minutes"),
            "observations": self.observations.get(),
        }
        if include_status:
            payload["status"] = self.status_choice.require_value().value
        return payload

    def _start_at(self) -> datetime:
        return datetime.fromisoformat(f"{self.date_text.get()}T{self.time_text.get()}")

    def _selected_code(self) -> str:
        selected = self.booking_table.selected_item()
        if selected is not None:
            return selected.code
        return self.code.get().strip()


class HistoryFrame(ViewFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller
        self.animal_choice: ChoiceBox[str]
        self.details = tk.StringVar()
        self.table: DataTable[Booking]
        self._build()
        self.refresh()

    def _build(self) -> None:
        ttk.Label(self, text="Histórico do animal", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        filters = ttk.Frame(self)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Animal").pack(side="left", padx=(0, 6))
        self.animal_choice = ChoiceBox(filters, (), width=34)
        self.animal_choice.pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Consultar", command=self.load_history).pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Atualizar", command=self.refresh).pack(side="left")
        ttk.Label(self, textvariable=self.details).pack(anchor="w", pady=(0, 8))
        self.table = DataTable(
            self,
            (
                Column("code", "Código", 90),
                Column("animal", "Animal", 100),
                Column("services", "Serviços", 180),
                Column("start", "Início", 130),
                Column("end", "Término", 130),
                Column("total", "Total", 90),
                Column("status", "Status", 110),
            ),
            booking_row,
        )
        self.table.pack(fill="both", expand=True)

    def refresh(self) -> None:
        animals = self.controller.get_animals()
        self.animal_choice.set_choices(animal_choices(animals))
        if animals:
            self.load_history()

    def load_history(self) -> None:
        try:
            animal_code = self.animal_choice.require_value()
            animal = self.controller.get_animal(animal_code)
            self.details.set(
                f"{animal.name} | {species_label(animal.species)} | "
                f"{animal_status_label(animal.status)} | {animal_details(animal)}"
            )
            self.table.set_items(self.controller.get_animal_history(animal_code))
        except Exception as error:
            self.show_error(error)

