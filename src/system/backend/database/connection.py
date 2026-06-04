from __future__ import annotations

import sqlite3
from pathlib import Path


DEFAULT_DATABASE_PATH = Path(".data") / "vehicle_rental.sqlite3"


class Database:
    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS vehicles (
                    plate TEXT PRIMARY KEY,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    daily_rate REAL NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('available', 'rented'))
                );

                CREATE TABLE IF NOT EXISTS customers (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    address TEXT NOT NULL,
                    password TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS rentals (
                    rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_code TEXT NOT NULL,
                    vehicle_plate TEXT NOT NULL,
                    pickup_date TEXT NOT NULL,
                    expected_return_date TEXT NOT NULL,
                    days INTEGER NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('active', 'finished')),
                    FOREIGN KEY(customer_code) REFERENCES customers(code) ON DELETE RESTRICT,
                    FOREIGN KEY(vehicle_plate) REFERENCES vehicles(plate) ON DELETE RESTRICT
                );
                """
            )
