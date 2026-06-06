from .frontend import RentalSystemApp
from system.backend.controllers import AppController
from system.backend.database import Database


def main() -> None:
    database = Database(".vehicle_rental.sqlite3")
    controller = AppController(database)
    app = RentalSystemApp(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
