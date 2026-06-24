import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class Database:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tutors (
                    cpf TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    address TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS animals (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    species TEXT NOT NULL CHECK(species IN ('dog', 'cat', 'bird')),
                    breed TEXT NOT NULL,
                    birthday TEXT NOT NULL,
                    weight REAL NOT NULL,
                    tutor_cpf TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('active', 'inactive')),
                    dog_size TEXT,
                    rabies_vaccinated INTEGER,
                    cat_neutered INTEGER,
                    cat_hair_type TEXT,
                    bird_leg_band TEXT,
                    bird_exotic INTEGER,
                    FOREIGN KEY(tutor_cpf) REFERENCES tutors(cpf) ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS services (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    service_type TEXT NOT NULL CHECK(service_type IN (
                        'consultation', 'bath_grooming', 'vaccination', 'exam', 'surgery', 'housing'
                    )),
                    description TEXT NOT NULL,
                    base_value REAL NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    veterinarian TEXT,
                    specialty TEXT,
                    nail_clipping INTEGER,
                    perfume INTEGER,
                    batch TEXT,
                    expiration_date TEXT,
                    laboratory TEXT,
                    daily_rate REAL,
                    accommodation_capacity INTEGER
                );

                CREATE TABLE IF NOT EXISTS bookings (
                    code TEXT PRIMARY KEY,
                    animal_code TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    total_value REAL NOT NULL,
                    status TEXT NOT NULL CHECK(status IN (
                        'booked', 'in_progress', 'completed', 'canceled', 'missed'
                    )),
                    observations TEXT NOT NULL,
                    FOREIGN KEY(animal_code) REFERENCES animals(code) ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS booking_services (
                    booking_code TEXT NOT NULL,
                    service_code TEXT NOT NULL,
                    service_order INTEGER NOT NULL,
                    PRIMARY KEY (booking_code, service_code, service_order),
                    FOREIGN KEY(booking_code) REFERENCES bookings(code) ON DELETE CASCADE,
                    FOREIGN KEY(service_code) REFERENCES services(code) ON DELETE RESTRICT
                );
                """
            )
