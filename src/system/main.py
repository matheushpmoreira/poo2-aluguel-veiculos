from .frontend import RentalSystemApp
from system.backend.controllers import AppController
from system.backend.database import Database


def get_controller() -> AppController:
    database = Database(".vehicle_rental.sqlite3")
    return AppController(database)


def main() -> None:
    app = RentalSystemApp(get_controller())
    app.mainloop()


if __name__ == "__main__":
    main()
