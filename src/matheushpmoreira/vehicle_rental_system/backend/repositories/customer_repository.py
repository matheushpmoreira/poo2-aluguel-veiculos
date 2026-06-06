
from matheushpmoreira.vehicle_rental_system.backend.database import Database
from matheushpmoreira.vehicle_rental_system.backend.errors import NotFoundError
from matheushpmoreira.vehicle_rental_system.backend.models.customer import Customer


class CustomerRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, customer: Customer) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO customers (code, name, phone, email, address, password)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (customer.code, customer.name, customer.phone, customer.email, customer.address, customer.password),
            )

    def update(self, customer: Customer) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE customers
                SET name = ?, phone = ?, email = ?, address = ?, password = ?
                WHERE code = ?
                """,
                (customer.name, customer.phone, customer.email, customer.address, customer.password, customer.code),
            )

            if cursor.rowcount == 0:
                raise NotFoundError("Cliente não encontrado.")

    def delete(self, code: str) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM customers WHERE code = ?", (code.strip(),))
            if cursor.rowcount == 0:
                raise NotFoundError("Cliente não encontrado.")

    def get_by_code(self, code: str) -> Customer | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM customers WHERE code = ?", (code.strip(),)).fetchone()
        return self._parse_row(row) if row else None

    def get_all(self) -> list[Customer]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM customers ORDER BY name").fetchall()
        return [self._parse_row(row) for row in rows]

    @staticmethod
    def _parse_row(row) -> Customer:
        return Customer(
            code=row["code"],
            name=row["name"],
            phone=row["phone"],
            email=row["email"],
            address=row["address"],
            password=row["password"],
        )
