import sqlite3
from datetime import date

from clivet.database import Database
from clivet.errors import ConflictError, NotFoundError
from clivet.models import Animal, Bird, Cat, Dog, Species


class AnimalRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, animal: Animal) -> None:
        try:
            with self.database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO animals (
                        code, name, species, breed, birthday, weight, tutor_cpf, status,
                        dog_size, rabies_vaccinated, cat_neutered, cat_hair_type,
                        bird_leg_band, bird_exotic
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._params(animal),
                )
        except sqlite3.IntegrityError as exc:
            if "FOREIGN KEY" in str(exc):
                raise NotFoundError("O animal exige um tutor cadastrado.") from exc
            raise ConflictError("Já existe um animal com este código.") from exc

    def update(self, animal: Animal) -> None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE animals
                SET name = ?, species = ?, breed = ?, birthday = ?, weight = ?, tutor_cpf = ?, status = ?,
                    dog_size = ?, rabies_vaccinated = ?, cat_neutered = ?, cat_hair_type = ?,
                    bird_leg_band = ?, bird_exotic = ?
                WHERE code = ?
                """,
                (
                    animal.name,
                    animal.species.value,
                    animal.breed,
                    animal.birthday.isoformat(),
                    animal.weight,
                    animal.tutor_cpf,
                    animal.status.value,
                    getattr(animal, "size", None),
                    1 if getattr(animal, "rabies_vaccinated", False) else 0,
                    1 if getattr(animal, "neutered", False) else 0,
                    getattr(animal, "hair_type", None),
                    getattr(animal, "leg_band", ""),
                    1 if getattr(animal, "exotic", False) else 0,
                    animal.code,
                ),
            )
            if cursor.rowcount == 0:
                raise NotFoundError("Animal não encontrado.")

    def delete(self, code: str) -> None:
        try:
            with self.database.connect() as connection:
                cursor = connection.execute("DELETE FROM animals WHERE code = ?", (code.strip().upper(),))
                if cursor.rowcount == 0:
                    raise NotFoundError("Animal não encontrado.")
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Não é possível remover um animal com agendamentos cadastrados.") from exc

    def get(self, code: str) -> Animal | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM animals WHERE code = ?", (code.strip().upper(),)).fetchone()
        return self._parse_row(row) if row else None

    def list(self, tutor_cpf: str = "") -> list[Animal]:
        params: tuple[str, ...] = ()
        where = ""
        if tutor_cpf.strip():
            where = "WHERE tutor_cpf = ?"
            params = (tutor_cpf.strip(),)
        with self.database.connect() as connection:
            rows = connection.execute(f"SELECT * FROM animals {where} ORDER BY name", params).fetchall()
        return [self._parse_row(row) for row in rows]

    @staticmethod
    def _params(animal: Animal) -> tuple[object, ...]:
        return (
            animal.code,
            animal.name,
            animal.species.value,
            animal.breed,
            animal.birthday.isoformat(),
            animal.weight,
            animal.tutor_cpf,
            animal.status.value,
            getattr(animal, "size", None),
            1 if getattr(animal, "rabies_vaccinated", False) else 0,
            1 if getattr(animal, "neutered", False) else 0,
            getattr(animal, "hair_type", None),
            getattr(animal, "leg_band", ""),
            1 if getattr(animal, "exotic", False) else 0,
        )

    @staticmethod
    def _parse_row(row: sqlite3.Row) -> Animal:
        base = {
            "code": row["code"],
            "name": row["name"],
            "species": row["species"],
            "breed": row["breed"],
            "birthday": date.fromisoformat(row["birthday"]),
            "weight": row["weight"],
            "tutor_cpf": row["tutor_cpf"],
            "status": row["status"],
        }
        species = Species(row["species"])
        if species == Species.DOG:
            return Dog(
                **base,
                size=row["dog_size"] or "medium",
                rabies_vaccinated=bool(int(row["rabies_vaccinated"] or 0)),
            )
        if species == Species.CAT:
            return Cat(
                **base,
                neutered=bool(int(row["cat_neutered"] or 0)),
                hair_type=row["cat_hair_type"] or "short",
            )
        return Bird(
            **base,
            leg_band=row["bird_leg_band"] or "",
            exotic=bool(int(row["bird_exotic"] or 0)),
        )
