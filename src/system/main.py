from .frontend import RentalSystemApp


def main() -> None:
    app = RentalSystemApp()
    app.mainloop()


if __name__ == "__main__":
    main()
