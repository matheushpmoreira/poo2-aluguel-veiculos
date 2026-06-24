from clivet.backend.controllers import AppController
from clivet.backend.database import Database
from clivet.frontend import RentalSystemApp


def main() -> None:
    database = Database(".vehicle_rental.sqlite3")
    controller = AppController(database)
    app = RentalSystemApp(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
