from pathlib import Path

from clivet.controllers import AppController
from clivet.database import Database


def main() -> None:
    path = Path(".clivet.sqlite3")
    path.unlink(missing_ok=True)
    controller = AppController(Database(path))

    tutors = [
        {
            "cpf": "123.456.789-00",
            "name": "João Silva",
            "phone": "(48) 99999-0000",
            "email": "joao@example.com",
            "address": "Rua das Flores, 100",
        },
        {
            "cpf": "987.654.321-00",
            "name": "Maria Souza",
            "phone": "(48) 98888-0000",
            "email": "maria@example.com",
            "address": "Rua Central, 200",
        },
        {
            "cpf": "456.123.789-00",
            "name": "Carla Mendes",
            "phone": "(48) 97777-0000",
            "email": "carla@example.com",
            "address": "Avenida Beira-Mar, 350",
        },
        {
            "cpf": "321.654.987-00",
            "name": "Bruno Rocha",
            "phone": "(48) 96666-0000",
            "email": "bruno@example.com",
            "address": "Rua das Palmeiras, 42",
        },
    ]

    animals = [
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
        },
        {
            "code": "BELA001",
            "name": "Bela",
            "species": "dog",
            "breed": "Golden retriever",
            "birthday": "2020-09-18",
            "weight": 27.0,
            "tutor_cpf": "456.123.789-00",
            "status": "active",
            "dog_size": "large",
            "rabies_vaccinated": True,
        },
        {
            "code": "TOBI001",
            "name": "Tobi",
            "species": "dog",
            "breed": "SRD",
            "birthday": "2022-02-03",
            "weight": 11.4,
            "tutor_cpf": "321.654.987-00",
            "status": "active",
            "dog_size": "small",
            "rabies_vaccinated": False,
        },
        {
            "code": "NINA001",
            "name": "Nina",
            "species": "dog",
            "breed": "Poodle",
            "birthday": "2019-12-22",
            "weight": 8.2,
            "tutor_cpf": "987.654.321-00",
            "status": "active",
            "dog_size": "small",
            "rabies_vaccinated": True,
        },
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
        },
        {
            "code": "LUA001",
            "name": "Lua",
            "species": "cat",
            "breed": "Siamês",
            "birthday": "2021-07-11",
            "weight": 3.9,
            "tutor_cpf": "123.456.789-00",
            "status": "active",
            "cat_neutered": False,
            "cat_hair_type": "short",
        },
        {
            "code": "FELIX001",
            "name": "Félix",
            "species": "cat",
            "breed": "Persa",
            "birthday": "2018-03-15",
            "weight": 5.6,
            "tutor_cpf": "456.123.789-00",
            "status": "active",
            "cat_neutered": True,
            "cat_hair_type": "long",
        },
        {
            "code": "PIPO001",
            "name": "Pipo",
            "species": "bird",
            "breed": "Calopsita",
            "birthday": "2022-08-05",
            "weight": 0.09,
            "tutor_cpf": "321.654.987-00",
            "status": "active",
            "bird_leg_band": "BR-2022-001",
            "bird_exotic": False,
        },
        {
            "code": "KIWI001",
            "name": "Kiwi",
            "species": "bird",
            "breed": "Periquito",
            "birthday": "2024-01-30",
            "weight": 0.04,
            "tutor_cpf": "123.456.789-00",
            "status": "active",
            "bird_leg_band": "BR-2024-014",
            "bird_exotic": False,
        },
        {
            "code": "LOLA001",
            "name": "Lola",
            "species": "bird",
            "breed": "Papagaio",
            "birthday": "2017-06-12",
            "weight": 0.38,
            "tutor_cpf": "987.654.321-00",
            "status": "inactive",
            "bird_leg_band": "BR-2017-088",
            "bird_exotic": True,
        },
    ]

    services = [
        {
            "code": "CONS001",
            "name": "Consulta veterinária",
            "service_type": "consultation",
            "description": "Atendimento clínico geral",
            "base_value": 150.0,
            "duration_minutes": 30,
            "veterinarian": "Dra. Ana",
            "specialty": "Clínica geral",
        },
        {
            "code": "CONS002",
            "name": "Consulta especializada",
            "service_type": "consultation",
            "description": "Atendimento com especialista",
            "base_value": 220.0,
            "duration_minutes": 45,
            "veterinarian": "Dr. Bruno",
            "specialty": "Dermatologia",
        },
        {
            "code": "BANHO001",
            "name": "Banho",
            "service_type": "bath_grooming",
            "description": "Banho simples com secagem",
            "base_value": 80.0,
            "duration_minutes": 60,
            "nail_clipping": True,
            "perfume": True,
        },
        {
            "code": "VAC001",
            "name": "Vacinação anual",
            "service_type": "vaccination",
            "description": "Aplicação de vacina anual",
            "base_value": 120.0,
            "duration_minutes": 20,
            "batch": "VAC-2026-A",
            "expiration_date": "2027-05-31",
            "laboratory": "VetLab",
        },
        {
            "code": "EXAM001",
            "name": "Exame laboratorial",
            "service_type": "exam",
            "description": "Coleta e análise laboratorial",
            "base_value": 95.0,
            "duration_minutes": 25,
        },
        {
            "code": "HOSP001",
            "name": "Hospedagem diária",
            "service_type": "housing",
            "description": "Hospedagem com alimentação inclusa",
            "base_value": 180.0,
            "duration_minutes": 1440,
            "daily_rate": 180.0,
            "accommodation_capacity": 6,
        },
    ]

    bookings = [
        {
            "code": "AG001",
            "animal_code": "REX001",
            "service_codes": ["CONS001", "BANHO001"],
            "start_at": "2026-07-01 09:00",
            "observations": "Primeiro atendimento.",
        },
        {
            "code": "AG002",
            "animal_code": "MIMI001",
            "service_codes": ["CONS002"],
            "start_at": "2026-07-01 10:00",
            "observations": "Avaliar alergia de pele.",
        },
        {
            "code": "AG003",
            "animal_code": "BELA001",
            "service_codes": ["BANHO001"],
            "start_at": "2026-07-01 11:00",
            "observations": "Usar shampoo para pele sensível.",
        },
        {
            "code": "AG004",
            "animal_code": "PIPO001",
            "service_codes": ["EXAM001"],
            "start_at": "2026-07-01 14:00",
            "observations": "Exame de rotina.",
        },
        {
            "code": "AG005",
            "animal_code": "REX001",
            "service_codes": ["VAC001"],
            "start_at": "2026-07-02 09:00",
            "observations": "Aplicar reforço anual.",
        },
        {
            "code": "AG006",
            "animal_code": "LUA001",
            "service_codes": ["CONS001"],
            "start_at": "2026-07-02 10:00",
            "observations": "Consulta por perda de apetite.",
        },
        {
            "code": "AG007",
            "animal_code": "TOBI001",
            "service_codes": ["CONS002", "VAC001"],
            "start_at": "2026-07-02 11:00",
            "observations": "Consulta dermatológica e vacina.",
        },
        {
            "code": "AG008",
            "animal_code": "MIMI001",
            "service_codes": ["EXAM001"],
            "start_at": "2026-07-03 09:00",
            "observations": "Retorno para exames.",
        },
        {
            "code": "AG009",
            "animal_code": "KIWI001",
            "service_codes": ["CONS001"],
            "start_at": "2026-07-03 10:00",
            "observations": "Avaliar muda de penas.",
        },
        {
            "code": "AG010",
            "animal_code": "BELA001",
            "service_codes": ["CONS002"],
            "start_at": "2026-07-03 14:00",
            "observations": "Retorno dermatológico.",
        },
        {
            "code": "AG011",
            "animal_code": "NINA001",
            "service_codes": ["BANHO001", "VAC001"],
            "start_at": "2026-07-04 09:00",
            "observations": "Banho e vacina.",
        },
        {
            "code": "AG012",
            "animal_code": "FELIX001",
            "service_codes": ["HOSP001"],
            "start_at": "2026-07-05 08:00",
            "observations": "Hospedagem por uma diária.",
        },
    ]

    for tutor in tutors:
        controller.post_tutor(tutor)
    for animal in animals:
        controller.post_animal(animal)
    for service in services:
        controller.post_service(service)
    for booking in bookings:
        controller.post_booking(booking)

    controller.complete_booking("AG001")
    controller.cancel_booking("AG003")
    controller.mark_booking_missed("AG008")


if __name__ == "__main__":
    main()
