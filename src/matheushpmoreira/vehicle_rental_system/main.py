from matheushpmoreira.vehicle_rental_system.backend.controllers import AppController
from matheushpmoreira.vehicle_rental_system.backend.database import Database
from matheushpmoreira.vehicle_rental_system.frontend import RentalSystemApp


def main() -> None:
    database = Database(".vehicle_rental.sqlite3")
    controller = AppController(database)
    app = RentalSystemApp(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
