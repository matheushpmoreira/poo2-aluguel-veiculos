from __future__ import annotations

import csv
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from system.backend.controllers import AppController


VEHICLE_TYPES = ("car", "motorcycle", "pickup truck", "van")
VEHICLE_STATUSES = ("available", "rented")


class RentalSystemApp(tk.Tk):
    def __init__(self, controller: AppController | None = None) -> None:
        super().__init__()
        self.controller = controller or AppController()
        self.title("Vehicle Rental System")
        self.geometry("1120x720")
        self.minsize(980, 620)
        self._configure_style()
        self._build_layout()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=(10, 6))
        style.configure("Treeview", rowheight=26)
        style.configure("Title.TLabel", font=("TkDefaultFont", 14, "bold"))

    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        notebook.add(AdminPanel(notebook, self.controller), text="Admin Panel")
        notebook.add(PublicArea(notebook, self.controller), text="Public Area")


class BaseFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, padding=10)
        self.controller = controller

    def show_error(self, error: Exception) -> None:
        messagebox.showerror("Error", str(error))

    def show_success(self, message: str) -> None:
        messagebox.showinfo("Success", message)


class AdminPanel(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        header = ttk.Label(self, text="Administrative operations", style="Title.TLabel")
        header.pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        self.vehicle_frame = VehicleAdminFrame(notebook, controller)
        self.customer_frame = CustomerAdminFrame(notebook, controller)
        self.rental_frame = RentalAdminFrame(notebook, controller)
        self.report_frame = ReportFrame(notebook, controller)
        notebook.add(self.vehicle_frame, text="Vehicles")
        notebook.add(self.customer_frame, text="Customers")
        notebook.add(self.rental_frame, text="Rentals")
        notebook.add(self.report_frame, text="Reports")
        notebook.bind("<<NotebookTabChanged>>", self._refresh_current_tab)

    def _refresh_current_tab(self, _event: tk.Event) -> None:
        for frame in (self.vehicle_frame, self.customer_frame, self.rental_frame, self.report_frame):
            if hasattr(frame, "refresh"):
                frame.refresh()


class VehicleAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.fields = {
            "plate": tk.StringVar(),
            "brand": tk.StringVar(),
            "model": tk.StringVar(),
            "year": tk.StringVar(),
            "vehicle_type": tk.StringVar(value=VEHICLE_TYPES[0]),
            "daily_rate": tk.StringVar(),
            "status": tk.StringVar(value=VEHICLE_STATUSES[0]),
        }
        self.search_text = tk.StringVar()
        self.search_status = tk.StringVar()
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Vehicle registration", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        self._entry(form, "Plate", "plate", 0)
        self._entry(form, "Brand", "brand", 1)
        self._entry(form, "Model", "model", 2)
        self._entry(form, "Year", "year", 3)
        ttk.Label(form, text="Type").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Combobox(form, textvariable=self.fields["vehicle_type"], values=VEHICLE_TYPES, state="readonly").grid(
            row=4, column=1, sticky="ew", pady=3
        )
        self._entry(form, "Daily rate", "daily_rate", 5)
        ttk.Label(form, text="Status").grid(row=6, column=0, sticky="w", pady=3)
        ttk.Combobox(form, textvariable=self.fields["status"], values=VEHICLE_STATUSES, state="readonly").grid(
            row=6, column=1, sticky="ew", pady=3
        )
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(form)
        buttons.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Create", command=self.create_vehicle).pack(fill="x", pady=2)
        ttk.Button(buttons, text="Update", command=self.update_vehicle).pack(fill="x", pady=2)
        ttk.Button(buttons, text="Delete", command=self.delete_vehicle).pack(fill="x", pady=2)
        ttk.Button(buttons, text="Clear", command=self.clear_form).pack(fill="x", pady=2)

        list_area = ttk.Frame(container)
        list_area.pack(side="left", fill="both", expand=True)
        filters = ttk.Frame(list_area)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Entry(filters, textvariable=self.search_text).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Combobox(
            filters, textvariable=self.search_status, values=("", *VEHICLE_STATUSES), state="readonly", width=14
        ).pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Search", command=self.refresh).pack(side="left")

        self.tree = ttk.Treeview(
            list_area,
            columns=("plate", "brand", "model", "year", "type", "rate", "status"),
            show="headings",
        )
        for column, title, width in (
            ("plate", "Plate", 90),
            ("brand", "Brand", 120),
            ("model", "Model", 140),
            ("year", "Year", 70),
            ("type", "Type", 110),
            ("rate", "Daily rate", 90),
            ("status", "Status", 90),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.fill_from_selection)

    def _entry(self, parent: ttk.Frame, label: str, key: str, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=self.fields[key]).grid(row=row, column=1, sticky="ew", pady=3)

    def create_vehicle(self) -> None:
        try:
            self.controller.post_vehicle(self._values())
            self.show_success("Vehicle created.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update_vehicle(self) -> None:
        try:
            self.controller.put_vehicle(self.fields["plate"].get(), self._values())
            self.show_success("Vehicle updated.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete_vehicle(self) -> None:
        try:
            self.controller.delete_vehicle(self.fields["plate"].get())
            self.show_success("Vehicle deleted.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        search_text = self.search_text.get()
        vehicles = self.controller.get_vehicles({"q": search_text, "status": self.search_status.get()})
        for vehicle in vehicles:
            self.tree.insert(
                "",
                "end",
                values=(
                    vehicle.plate,
                    vehicle.brand,
                    vehicle.model,
                    vehicle.year,
                    vehicle.vehicle_type,
                    f"{vehicle.daily_rate:.2f}",
                    vehicle.status,
                ),
            )

    def fill_from_selection(self, _event: tk.Event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        for key, value in zip(self.fields, values, strict=True):
            self.fields[key].set(value)

    def clear_form(self) -> None:
        for key, variable in self.fields.items():
            variable.set("")
        self.fields["vehicle_type"].set(VEHICLE_TYPES[0])
        self.fields["status"].set(VEHICLE_STATUSES[0])

    def _values(self) -> dict[str, str]:
        return {key: variable.get() for key, variable in self.fields.items()}


class CustomerAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.fields = {
            "code": tk.StringVar(),
            "name": tk.StringVar(),
            "phone": tk.StringVar(),
            "email": tk.StringVar(),
            "address": tk.StringVar(),
            "password": tk.StringVar(),
        }
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Customer registration", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))
        for row, (key, label) in enumerate(
            (
                ("code", "Code or CPF"),
                ("name", "Name"),
                ("phone", "Phone"),
                ("email", "Email"),
                ("address", "Address"),
                ("password", "Password"),
            )
        ):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=self.fields[key]).grid(row=row, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(form)
        buttons.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Create", command=self.create_customer).pack(fill="x", pady=2)
        ttk.Button(buttons, text="Update", command=self.update_customer).pack(fill="x", pady=2)
        ttk.Button(buttons, text="Delete", command=self.delete_customer).pack(fill="x", pady=2)
        ttk.Button(buttons, text="Clear", command=self.clear_form).pack(fill="x", pady=2)

        self.tree = ttk.Treeview(
            container,
            columns=("code", "name", "phone", "email", "address", "password"),
            show="headings",
        )
        for column, title, width in (
            ("code", "Code", 110),
            ("name", "Name", 160),
            ("phone", "Phone", 110),
            ("email", "Email", 180),
            ("address", "Address", 220),
            ("password", "Password", 100),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.fill_from_selection)

    def create_customer(self) -> None:
        try:
            self.controller.post_customer(self._values())
            self.show_success("Customer created.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def update_customer(self) -> None:
        try:
            self.controller.put_customer(self.fields["code"].get(), self._values())
            self.show_success("Customer updated.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def delete_customer(self) -> None:
        try:
            self.controller.delete_customer(self.fields["code"].get())
            self.show_success("Customer deleted.")
            self.clear_form()
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for customer in self.controller.get_customers():
            self.tree.insert(
                "",
                "end",
                values=(
                    customer.code,
                    customer.name,
                    customer.phone,
                    customer.email,
                    customer.address,
                    customer.password,
                ),
            )

    def fill_from_selection(self, _event: tk.Event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        for key, value in zip(self.fields, values, strict=True):
            self.fields[key].set(value)

    def clear_form(self) -> None:
        for variable in self.fields.values():
            variable.set("")

    def _values(self) -> dict[str, str]:
        return {key: variable.get() for key, variable in self.fields.items()}


class RentalAdminFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.customer_value = tk.StringVar()
        self.vehicle_value = tk.StringVar()
        self.pickup_date = tk.StringVar(value=date.today().isoformat())
        self.days = tk.StringVar(value="1")
        self.customer_options: dict[str, str] = {}
        self.vehicle_options: dict[str, str] = {}
        self._build()
        self.refresh()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        form = ttk.LabelFrame(container, text="Create rental", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(form, text="Customer").grid(row=0, column=0, sticky="w", pady=3)
        self.customer_combo = ttk.Combobox(form, textvariable=self.customer_value, state="readonly", width=34)
        self.customer_combo.grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Vehicle").grid(row=1, column=0, sticky="w", pady=3)
        self.vehicle_combo = ttk.Combobox(form, textvariable=self.vehicle_value, state="readonly", width=34)
        self.vehicle_combo.grid(row=1, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Pickup date").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.pickup_date).grid(row=2, column=1, sticky="ew", pady=3)
        ttk.Label(form, text="Days").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.days).grid(row=3, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)

        ttk.Button(form, text="Create rental", command=self.create_rental).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(10, 2)
        )
        ttk.Button(form, text="Finish selected rental", command=self.finish_selected).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=2
        )

        self.tree = ttk.Treeview(
            container,
            columns=("id", "customer", "vehicle", "pickup", "return", "days", "total", "status"),
            show="headings",
        )
        for column, title, width in (
            ("id", "ID", 60),
            ("customer", "Customer", 120),
            ("vehicle", "Vehicle", 100),
            ("pickup", "Pickup", 100),
            ("return", "Expected return", 120),
            ("days", "Days", 70),
            ("total", "Total", 90),
            ("status", "Status", 90),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width)
        self.tree.pack(side="left", fill="both", expand=True)

    def create_rental(self) -> None:
        try:
            customer_code = self.customer_options[self.customer_value.get()]
            vehicle_plate = self.vehicle_options[self.vehicle_value.get()]
            rental = self.controller.post_rental(
                {
                    "customer_code": customer_code,
                    "vehicle_plate": vehicle_plate,
                    "pickup_date": self.pickup_date.get(),
                    "days": self.days.get(),
                }
            )
            self.show_success(f"Rental {rental.rental_id} created. Total: {rental.total_amount:.2f}")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def finish_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection required", "Select a rental first.")
            return
        rental_id = self.tree.item(selected[0], "values")[0]
        try:
            self.controller.post_rental_finish(rental_id)
            self.show_success("Rental finished.")
            self.refresh()
        except Exception as error:
            self.show_error(error)

    def refresh(self) -> None:
        customers = self.controller.get_customers()
        vehicles = self.controller.get_vehicles({"status": "available"})
        self.customer_options = {f"{customer.code} - {customer.name}": customer.code for customer in customers}
        self.vehicle_options = {
            f"{vehicle.plate} - {vehicle.brand} {vehicle.model} ({vehicle.daily_rate:.2f})": vehicle.plate
            for vehicle in vehicles
        }
        self.customer_combo["values"] = tuple(self.customer_options)
        self.vehicle_combo["values"] = tuple(self.vehicle_options)
        if self.customer_options and self.customer_value.get() not in self.customer_options:
            self.customer_value.set(next(iter(self.customer_options)))
        if self.vehicle_options and self.vehicle_value.get() not in self.vehicle_options:
            self.vehicle_value.set(next(iter(self.vehicle_options)))

        self.tree.delete(*self.tree.get_children())
        for rental in self.controller.get_rentals():
            self.tree.insert(
                "",
                "end",
                values=(
                    rental.rental_id,
                    rental.customer_code,
                    rental.vehicle_plate,
                    rental.pickup_date.isoformat(),
                    rental.expected_return_date.isoformat(),
                    rental.days,
                    f"{rental.total_amount:.2f}",
                    rental.status,
                ),
            )


class ReportFrame(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self._build()
        self.refresh()

    def _build(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Export CSV", command=self.export_csv).pack(side="left")

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)

        available_box = ttk.LabelFrame(panes, text="Available vehicles", padding=8)
        active_box = ttk.LabelFrame(panes, text="Active rentals", padding=8)
        panes.add(available_box, weight=1)
        panes.add(active_box, weight=1)

        self.available_tree = ttk.Treeview(
            available_box,
            columns=("plate", "brand", "model", "type", "rate"),
            show="headings",
        )
        for column, title in (
            ("plate", "Plate"),
            ("brand", "Brand"),
            ("model", "Model"),
            ("type", "Type"),
            ("rate", "Daily rate"),
        ):
            self.available_tree.heading(column, text=title)
            self.available_tree.column(column, width=110)
        self.available_tree.pack(fill="both", expand=True)

        self.active_tree = ttk.Treeview(
            active_box,
            columns=("id", "customer", "vehicle", "return", "total", "late_fee"),
            show="headings",
        )
        for column, title in (
            ("id", "ID"),
            ("customer", "Customer"),
            ("vehicle", "Vehicle"),
            ("return", "Expected return"),
            ("total", "Total"),
            ("late_fee", "Late fee"),
        ):
            self.active_tree.heading(column, text=title)
            self.active_tree.column(column, width=110)
        self.active_tree.pack(fill="both", expand=True)

    def refresh(self) -> None:
        self.available_tree.delete(*self.available_tree.get_children())
        self.active_tree.delete(*self.active_tree.get_children())
        for vehicle in self.controller.get_vehicles({"status": "available"}):
            self.available_tree.insert(
                "",
                "end",
                values=(vehicle.plate, vehicle.brand, vehicle.model, vehicle.vehicle_type, f"{vehicle.daily_rate:.2f}"),
            )
        for rental in self.controller.get_rentals({"status": "active"}):
            late_fee = self.controller.get_rental_late_fee(rental.rental_id or 0)
            self.active_tree.insert(
                "",
                "end",
                values=(
                    rental.rental_id,
                    rental.customer_code,
                    rental.vehicle_plate,
                    rental.expected_return_date.isoformat(),
                    f"{rental.total_amount:.2f}",
                    f"{late_fee:.2f}",
                ),
            )

    def export_csv(self) -> None:
        default_path = Path(".data") / "rental_report.csv"
        file_path = filedialog.asksaveasfilename(
            title="Export report",
            initialfile=default_path.name,
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Available vehicles"])
                writer.writerow(["plate", "brand", "model", "type", "daily_rate"])
                for vehicle in self.controller.get_vehicles({"status": "available"}):
                    writer.writerow(
                        [vehicle.plate, vehicle.brand, vehicle.model, vehicle.vehicle_type, f"{vehicle.daily_rate:.2f}"]
                    )
                writer.writerow([])
                writer.writerow(["Active rentals"])
                writer.writerow(["id", "customer", "vehicle", "expected_return", "total", "late_fee"])
                for rental in self.controller.get_rentals({"status": "active"}):
                    writer.writerow(
                        [
                            rental.rental_id,
                            rental.customer_code,
                            rental.vehicle_plate,
                            rental.expected_return_date.isoformat(),
                            f"{rental.total_amount:.2f}",
                            f"{self.controller.get_rental_late_fee(rental.rental_id or 0):.2f}",
                        ]
                    )
            self.show_success(f"Report exported to {file_path}.")
        except Exception as error:
            self.show_error(error)


class PublicArea(BaseFrame):
    def __init__(self, parent: tk.Widget, controller: AppController) -> None:
        super().__init__(parent, controller)
        self.customer = None
        self.code = tk.StringVar()
        self.password = tk.StringVar()
        self.pickup_date = tk.StringVar(value=date.today().isoformat())
        self.days = tk.StringVar(value="1")
        self.status_text = tk.StringVar(value="Not logged in")
        self._build()
        self.refresh_public_lists()

    def _build(self) -> None:
        login_box = ttk.LabelFrame(self, text="Customer login", padding=10)
        login_box.pack(fill="x", pady=(0, 8))
        ttk.Label(login_box, text="Code or CPF").pack(side="left", padx=(0, 6))
        ttk.Entry(login_box, textvariable=self.code, width=18).pack(side="left", padx=(0, 8))
        ttk.Label(login_box, text="Password").pack(side="left", padx=(0, 6))
        ttk.Entry(login_box, textvariable=self.password, show="*", width=18).pack(side="left", padx=(0, 8))
        ttk.Button(login_box, text="Login", command=self.login).pack(side="left", padx=(0, 6))
        ttk.Button(login_box, text="Logout", command=self.logout).pack(side="left", padx=(0, 12))
        ttk.Label(login_box, textvariable=self.status_text).pack(side="left")

        rental_box = ttk.LabelFrame(self, text="Rent a vehicle", padding=10)
        rental_box.pack(fill="x", pady=(0, 8))
        ttk.Label(rental_box, text="Pickup date").pack(side="left", padx=(0, 6))
        ttk.Entry(rental_box, textvariable=self.pickup_date, width=14).pack(side="left", padx=(0, 8))
        ttk.Label(rental_box, text="Days").pack(side="left", padx=(0, 6))
        ttk.Entry(rental_box, textvariable=self.days, width=8).pack(side="left", padx=(0, 8))
        ttk.Button(rental_box, text="Rent selected vehicle", command=self.create_customer_rental).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(rental_box, text="Refresh", command=self.refresh_public_lists).pack(side="left")

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)
        available_box = ttk.LabelFrame(panes, text="Available vehicles", padding=8)
        rentals_box = ttk.LabelFrame(panes, text="My rentals", padding=8)
        panes.add(available_box, weight=1)
        panes.add(rentals_box, weight=1)

        self.available_tree = ttk.Treeview(
            available_box,
            columns=("plate", "brand", "model", "year", "type", "rate"),
            show="headings",
        )
        for column, title in (
            ("plate", "Plate"),
            ("brand", "Brand"),
            ("model", "Model"),
            ("year", "Year"),
            ("type", "Type"),
            ("rate", "Daily rate"),
        ):
            self.available_tree.heading(column, text=title)
            self.available_tree.column(column, width=100)
        self.available_tree.pack(fill="both", expand=True)

        self.rental_tree = ttk.Treeview(
            rentals_box,
            columns=("id", "vehicle", "pickup", "return", "days", "total", "status"),
            show="headings",
        )
        for column, title in (
            ("id", "ID"),
            ("vehicle", "Vehicle"),
            ("pickup", "Pickup"),
            ("return", "Expected return"),
            ("days", "Days"),
            ("total", "Total"),
            ("status", "Status"),
        ):
            self.rental_tree.heading(column, text=title)
            self.rental_tree.column(column, width=100)
        self.rental_tree.pack(fill="both", expand=True)

    def login(self) -> None:
        try:
            self.customer = self.controller.post_customer_login(
                {"code": self.code.get(), "password": self.password.get()}
            )
            self.status_text.set(f"Logged in as {self.customer.name}")
            self.refresh_public_lists()
        except Exception as error:
            self.customer = None
            self.status_text.set("Not logged in")
            self.show_error(error)

    def logout(self) -> None:
        self.customer = None
        self.password.set("")
        self.status_text.set("Not logged in")
        self.refresh_public_lists()

    def create_customer_rental(self) -> None:
        if self.customer is None:
            messagebox.showwarning("Login required", "Customer login is required.")
            return
        selected = self.available_tree.selection()
        if not selected:
            messagebox.showwarning("Selection required", "Select an available vehicle first.")
            return
        vehicle_plate = self.available_tree.item(selected[0], "values")[0]
        try:
            rental = self.controller.post_rental(
                {
                    "customer_code": self.customer.code,
                    "vehicle_plate": vehicle_plate,
                    "pickup_date": self.pickup_date.get(),
                    "days": self.days.get(),
                }
            )
            self.show_success(f"Rental {rental.rental_id} created. Total: {rental.total_amount:.2f}")
            self.refresh_public_lists()
        except Exception as error:
            self.show_error(error)

    def refresh_public_lists(self) -> None:
        self.available_tree.delete(*self.available_tree.get_children())
        self.rental_tree.delete(*self.rental_tree.get_children())
        for vehicle in self.controller.get_vehicles({"status": "available"}):
            self.available_tree.insert(
                "",
                "end",
                values=(
                    vehicle.plate,
                    vehicle.brand,
                    vehicle.model,
                    vehicle.year,
                    vehicle.vehicle_type,
                    f"{vehicle.daily_rate:.2f}",
                ),
            )
        if self.customer is None:
            return
        for rental in self.controller.get_rentals({"customer_code": self.customer.code}):
            self.rental_tree.insert(
                "",
                "end",
                values=(
                    rental.rental_id,
                    rental.vehicle_plate,
                    rental.pickup_date.isoformat(),
                    rental.expected_return_date.isoformat(),
                    rental.days,
                    f"{rental.total_amount:.2f}",
                    rental.status,
                ),
            )
