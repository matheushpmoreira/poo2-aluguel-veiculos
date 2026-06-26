import sqlite3

from clivet.database import Database
from clivet.errors import ConflictError, NotFoundError
from clivet.models import Tutor


class TutorRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, tutor: Tutor) -> None:
        try:
            with self.database.connect() as connection:
                connection.execute(
                    "INSERT INTO tutors (cpf, name, phone, email, address) VALUES (?, ?, ?, ?, ?)",
                    (tutor.cpf, tutor.name, tutor.phone, tutor.email, tutor.address),
                )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Já existe um tutor com este CPF.") from exc

    def update(self, tutor: Tutor) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE tutors
                SET name = ?, phone = ?, email = ?, address = ?
                WHERE cpf = ?
                """,
                (tutor.name, tutor.phone, tutor.email, tutor.address, tutor.cpf),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Tutor não encontrado.")

    def delete(self, cpf: str) -> None:
        try:
            with self.database.connect() as connection:
                cursor = connection.execute("DELETE FROM tutors WHERE cpf = ?", (cpf.strip(),))
                if cursor.rowcount == 0:
                    raise NotFoundError("Tutor não encontrado.")
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Não é possível remover um tutor com animais cadastrados.") from exc

    def get(self, cpf: str) -> Tutor | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM tutors WHERE cpf = ?", (cpf.strip(),)).fetchone()
        return self._parse_row(row) if row else None

    def list(self) -> list[Tutor]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM tutors ORDER BY name").fetchall()
        return [self._parse_row(row) for row in rows]

    @staticmethod
    def _parse_row(row: sqlite3.Row) -> Tutor:
        return Tutor(
            cpf=row["cpf"],
            name=row["name"],
            phone=row["phone"],
            email=row["email"],
            address=row["address"],
        )
