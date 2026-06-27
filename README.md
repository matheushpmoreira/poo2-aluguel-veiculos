# Clivet - Clínica Veterinária

Sistema desktop para gerenciamento de clínica veterinária, desenvolvido em Python com interface gráfica em Tkinter e persistência em SQLite.

## Requisitos

- Python 3.14 ou superior
- Tkinter disponível na instalação do Python

## Executar

```bash
uv run clivet
```

O banco de dados SQLite é criado automaticamente em `.clivet.sqlite3`.

## Popular o banco de dados

```bash
PYTHONPATH=src python scripts/seed_database.py
```

O script cria tutores, animais, serviços e um agendamento de exemplo.

## Estrutura do projeto

- `clivet.models`: classes de domínio para tutores, animais, serviços e agendamentos.
- `clivet.repositories`: persistência em SQLite.
- `clivet.services`: regras de negócio e validações.
- `clivet.controllers`: fachada da aplicação usada pela interface.
- `clivet.views`: interface gráfica em Tkinter.
- `scripts/seed_database.py`: script de população do banco de dados.

## Funcionalidades principais

- Cadastro, listagem, edição e remoção de tutores, animais, serviços e agendamentos.
- Cadastro de animais com campos dinâmicos para cachorro, gato e ave.
- Cadastro de serviços com campos dinâmicos para consulta, banho/tosa, vacinação e hospedagem, além de tipos genéricos para exame e cirurgia.
- Agendamento com seleção de animal, múltiplos serviços, data e hora.
- Cálculo automático de término estimado e valor total.
- Acréscimo de 20% em agendamentos iniciados em fins de semana.
- Bloqueio de agendamentos para animais inativos.
- Bloqueio de agendamentos sobrepostos para o mesmo animal.
- Bloqueio de consultas sobrepostas com o mesmo veterinário.
- Histórico do animal com agendamentos concluídos, cancelados e faltantes.
- Persistência em SQLite.

## Checklist

### Critérios de avaliação

- [X] Modelagem orientada a objetos (classes, atributos, métodos)
- [X] Encapsulamento (atributos privados, getters/setters)
- [X] Herança (Animal → Cachorro/Gato/Ave; Serviço → Consulta/BanhoTosa/Vacinação/Hospedagem)
- [X] Polimorfismo implementado (sobrescrita de métodos nas subclasses)
- [X] Composição entre entidades (Agendamento composto por Animal + Serviços; Animal vinculado a Tutor)
- [X] Interface gráfica com Tkinter (janelas, navegação, campos, listas e mensagens)
- [X] Funcionalidades obrigatórias (CRUD de tutores, animais, serviços e agendamentos)
- [X] Regras de negócio implementadas (sobreposição de horários, cálculo automático, acréscimo de 20% em finais de semana, validações)
- [X] Persistência de dados (JSON ou SQLite, salvamento e carregamento corretos)
- [X] Organização do código e documentação (estrutura de pastas, README, relatório, comentários)

### Regras de negócio

- [X] Um animal inativo não pode ser agendado.
- [X] Um agendamento só pode ser criado se o tutor e o animal estiverem cadastrados.
- [X] Não pode haver sobreposição de horários para o mesmo animal (um animal não pode ter dois agendamentos no mesmo horário).
- [X] Não pode haver sobreposição de horários para serviços que exijam o mesmo recurso (ex: duas cirurgias no mesmo horário, ou consulta com o mesmo veterinário).
- [X] Ao criar um agendamento, o status inicial é "agendado".
- [X] Ao concluir um agendamento, o status muda para "concluído" e é registrado no histórico do animal.
- [X] O valor total deve ser calculado automaticamente, com acréscimo de 20% para agendamentos em sábados e domingos.
- [X] Não devem ser aceitos cadastros com campos obrigatórios vazios.
- [X] CPF do tutor e código do animal devem ser únicos no sistema.
- [X] Agendamentos cancelados ou não comparecidos devem ser mantidos no histórico.
