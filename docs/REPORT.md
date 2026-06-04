# Project Report

## Created classes

- `Vehicle`, `Car`, `Motorcycle`, `PickupTruck`, `Van`: vehicle hierarchy with plate, brand, model, year, type, daily rate and status.
- `Customer`: customer data and plain password validation for login.
- `Rental`: rental data, calculated total amount, status and references to customer and vehicle.
- Repository classes: `VehicleRepository`, `CustomerRepository`, `RentalRepository`.
- Service classes: `VehicleService`, `CustomerService`, `RentalService`.
- `AppController`: central facade that connects repositories and services.
- Tkinter classes: `RentalSystemApp`, `AdminPanel`, `VehicleAdminFrame`, `CustomerAdminFrame`, `RentalAdminFrame`, `ReportFrame`, `PublicArea`.

## Object-oriented programming concepts

- Classes and objects are used throughout the domain, persistence, services and interface.
- Attributes store entity state, such as `Vehicle.status` and `Rental.total_amount`.
- Methods implement behavior, such as `Vehicle.mark_as_rented`, `Rental.finish` and `Customer.check_password`.
- Encapsulation is applied by keeping validation and state changes inside model and service methods.
- Inheritance is represented by specialized vehicles inheriting from `Vehicle`.
- Polymorphism is used through the vehicle factory, which returns different vehicle subclasses through the same interface.
- Composition appears in `Rental`, which can hold related `Customer` and `Vehicle` objects.
- The system separates business logic from the graphical interface through backend services and controllers.

## Implemented business rules

- A rented vehicle cannot be rented again.
- A rental can only be created for a registered customer.
- A rental can only be created for a registered and available vehicle.
- Creating a rental changes the vehicle status to `rented`.
- Finishing a rental changes the vehicle status back to `available`.
- The rental total is calculated automatically from daily rate and number of days.
- Required fields are validated before records are saved.

## Extra features

- SQLite database stored in `.data`.
- Customer login with plain stored password, as requested.
- Public customer area separated from the administrative panel.
- Vehicle search by text and status.
- Available vehicle and active rental reports.
- Late fee calculation for overdue active rentals.
- CSV export for reports.
- Interface organized with `ttk.Notebook` tabs.
- Seed script and automated tests.

## Difficulties

The main challenge was keeping the desktop interface simple while still exposing all required operations. The solution uses separate tabs for each administrative area and a dedicated public area so the workflows stay clear.

## Future improvements

- Add stronger authentication and password hashing.
- Add rental date conflict checks for future reservations.
- Add PDF report export.
- Add richer validation for CPF, email and phone formats.
- Add pagination or advanced filters for large databases.

