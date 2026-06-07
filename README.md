# Sistema de Aluguel de Veículos

Sistema de aluguel de veículos desenvolvido em Python, com interface gráfica em Tkinter e persistência em SQLite.

## Requisitos

- Python 3.11 ou superior
- Tkinter disponível na instalação do Python

## Executar

```bash
uv run vhs
```

O banco de dados SQLite é criado automaticamente em `.vehicle_rental.sqlite3`.

## Popular o banco de dados

```bash
python scripts/seed_database.py
```

Exemplos de login de clientes cadastrados pelo script:

- Código: `11122233344`, senha: `ana123`
- Código: `55566677788`, senha: `bruno123`

## Estrutura do projeto

- `backend/models`: classes de domínio para veículos, clientes e aluguéis.
- `backend/repositories`: classes de persistência em SQLite.
- `backend/services`: regras de negócio e validações.
- `backend/controllers`: fachada da aplicação usada pela interface.
- `frontend`: interface gráfica em Tkinter.
- `scripts/seed_database.py`: script de população do banco de dados.

## Funcionalidades principais

- Cadastro de veículos, clientes e aluguéis.
- Listagem de veículos, clientes e aluguéis.
- Busca de veículos por placa, marca, modelo e status.
- Criação de aluguel com cálculo automático do valor total.
- Finalização de aluguel com atualização do status do veículo.
- Login de cliente na interface pública.
- Painel administrativo separado da área pública do cliente.
- Persistência em SQLite.
- Relatórios de veículos disponíveis e aluguéis ativos.
- Exportação de relatório em CSV.
- Cálculo de multa por atraso em aluguéis ativos vencidos.
