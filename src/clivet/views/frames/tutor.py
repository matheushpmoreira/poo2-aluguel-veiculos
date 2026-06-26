import tkinter as tk
from tkinter import ttk

from clivet.controllers import AppController
from clivet.models import *
from clivet.views.widgets import *


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
