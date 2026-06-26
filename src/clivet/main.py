from clivet.controllers import AppController
from clivet.database import Database
from clivet.views import PetClinicApp


def main() -> None:
    database = Database(".clivet.sqlite3")
    controller = AppController(database)
    app = PetClinicApp(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
