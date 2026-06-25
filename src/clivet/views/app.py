import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk

from clivet.controllers import AppController
from clivet.models import (
    Animal,
    AnimalStatus,
    BathGrooming,
    Bird,
    Booking,
    Cat,
    Consultation,
    Dog,
    Service,
    ServiceType,
    Species,
    Tutor,
    Vaccination,
)
from clivet.views.choices import (
    animal_choices,
    animal_status_choices,
    booking_status_choices,
    cat_hair_choices,
    dog_size_choices,
    service_type_choices,
    species_choices,
    tutor_choices,
)
from clivet.views.formatters import animal_details, animal_row, booking_row, service_row
from clivet.views.labels import (
    animal_status_label,
    booking_status_label,
    cat_hair_label,
    dog_size_label,
    money,
    service_type_label,
    species_label,
)
from clivet.views.widgets import ChoiceBox, Column, DataTable, DateEntry, ViewFrame

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

