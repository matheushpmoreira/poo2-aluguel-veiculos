import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk

from clivet.controllers import AppController
from clivet.models import *
from clivet.views.choices import *
from clivet.views.formatters import *
from clivet.views.labels import *
from clivet.views.widgets import *


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
