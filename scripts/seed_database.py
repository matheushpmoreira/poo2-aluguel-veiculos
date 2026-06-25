from pathlib import Path

from clivet.controllers import AppController
from clivet.database import Database


def main() -> None:
    path = Path(".clivet.sqlite3")
    path.unlink(missing_ok=True)
    controller = AppController(Database(path))

    controller.post_tutor(
        {
            "cpf": "123.456.789-00",
            "name": "João Silva",
            "phone": "(48) 99999-0000",
            "email": "joao@example.com",
            "address": "Rua das Flores, 100",
        }
    )
    controller.post_tutor(
        {
            "cpf": "987.654.321-00",
            "name": "Maria Souza",
            "phone": "(48) 98888-0000",
            "email": "maria@example.com",
            "address": "Rua Central, 200",
        }
    )

    controller.post_animal(
        {
            "code": "REX001",
            "name": "Rex",
            "species": "dog",
            "breed": "Pastor alemão",
            "birthday": "2021-05-10",
            "weight": 32.5,
            "tutor_cpf": "123.456.789-00",
            "status": "active",
            "dog_size": "large",
            "rabies_vaccinated": True,
        }
    )
    controller.post_animal(
        {
            "code": "MIMI001",
            "name": "Mimi",
            "species": "cat",
            "breed": "SRD",
            "birthday": "2023-01-20",
            "weight": 4.2,
            "tutor_cpf": "987.654.321-00",
            "status": "active",
            "cat_neutered": True,
            "cat_hair_type": "short",
        }
    )

    controller.post_service(
        {
            "code": "CONS001",
            "name": "Consulta veterinária",
            "service_type": "consultation",
            "description": "Atendimento clínico geral",
            "base_value": 150.0,
            "duration_minutes": 30,
            "veterinarian": "Dra. Ana",
            "specialty": "Clínica geral",
        }
    )
    controller.post_service(
        {
            "code": "BANHO001",
            "name": "Banho",
            "service_type": "bath_grooming",
            "description": "Banho simples",
            "base_value": 80.0,
            "duration_minutes": 60,
            "nail_clipping": True,
            "perfume": True,
        }
    )

    controller.post_booking(
        {
            "code": "AG001",
            "animal_code": "REX001",
            "service_codes": ["CONS001", "BANHO001"],
            "start_at": "2026-06-15 14:00",
            "observations": "Primeiro atendimento.",
        }
    )


if __name__ == "__main__":
    main()
