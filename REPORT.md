# Relatório do Projeto

Este projeto implementa um sistema desktop para gerenciamento de uma clínica veterinária, usando Python, Tkinter e SQLite.

A aplicação usa uma organização em camadas: modelos de domínio, repositórios de persistência, serviços com regras de negócio, controller de fachada e views em Tkinter. Os nomes internos ficam em inglês, enquanto a interface gráfica apresenta textos em português brasileiro.

## Classes principais

### Modelos

- `Tutor`: representa o responsável pelo animal, com CPF, nome, telefone, e-mail e endereço.
- `Animal`: classe base para animais, com código, nome, espécie, raça, nascimento, peso, tutor e status.
- `Dog`, `Cat` e `Bird`: especializações de `Animal` com campos próprios.
- `Service`: classe base para serviços da clínica, com código, nome, tipo, descrição, valor base e duração.
- `Consultation`, `BathGrooming`, `Vaccination` e `Housing`: especializações de `Service` com campos próprios. Exames e cirurgias usam a classe base `Service`.
- `Booking`: representa um agendamento com animal, serviços, início, término estimado, valor total, status e observações.
- Enums como `Species`, `AnimalStatus`, `ServiceType` e `BookingStatus` evitam valores livres inválidos.

### Persistência e regras

- `Database`: encapsula a conexão SQLite e cria as tabelas.
- `TutorRepository`, `AnimalRepository`, `ServiceRepository` e `BookingRepository`: traduzem linhas do banco em objetos e executam operações CRUD.
- `TutorService`, `AnimalService`, `ServiceCatalog` e `BookingService`: concentram validações e regras de negócio.
- `AppController`: expõe métodos de alto nível usados pela interface, como `post_tutor`, `post_animal`, `post_service`, `post_booking` e `complete_booking`.
- `AppError` e suas subclasses representam erros de validação, conflito e entidade não encontrada.

### Interface gráfica

- `PetClinicApp`: janela principal com abas.
- `TutorFrame`, `AnimalFrame`, `ServiceFrame`, `BookingFrame` e `HistoryFrame`: telas para cadastro, listagem, agendamento e histórico.
- `ChoiceBox`, `DataTable` e `DateEntry`: widgets auxiliares para comboboxes tipadas, tabelas e datas.

## Conceitos de POO utilizados

- Classes e objetos: tutores, animais, serviços e agendamentos são representados por objetos de domínio.
- Atributos e métodos: os modelos validam seus próprios campos e `Booking.create` calcula término e valor total.
- Encapsulamento: a interface acessa a lógica por meio de `AppController`; regras de negócio ficam nos serviços.
- Herança: `Dog`, `Cat` e `Bird` herdam de `Animal`; `Consultation`, `BathGrooming`, `Vaccination` e `Housing` herdam de `Service`.
- Polimorfismo: repositórios e views manipulam subclasses por meio das classes base `Animal` e `Service`.
- Composição: bookings são compostos por um animal e múltiplos serviços; controller, serviços e repositórios também são compostos entre si.

## Regras de negócio implementadas

- Campos obrigatórios são validados.
- CPF de tutor e código de animal são únicos.
- Um animal só pode ser cadastrado para um tutor existente.
- Um agendamento só pode ser criado para animal e serviços cadastrados.
- Animais inativos não podem ser agendados.
- O status inicial de agendamento é `booked`.
- O término estimado é calculado pela soma das durações dos serviços.
- O valor total é calculado pela soma dos valores base dos serviços.
- Agendamentos iniciados em sábado ou domingo recebem acréscimo de 20%.
- O mesmo animal não pode ter agendamentos sobrepostos, exceto registros cancelados ou faltantes.
- Consultas com o mesmo veterinário não podem ser sobrepostas.
- A ação de concluir altera o status diretamente para `completed`.
- Agendamentos cancelados e faltantes permanecem no histórico do animal.

## Persistência de dados

O sistema usa SQLite. O banco padrão é `.clivet.sqlite3`, criado automaticamente ao iniciar a aplicação. As tabelas principais são `tutors`, `animals`, `services`, `bookings` e `booking_services`.

O script `scripts/seed_database.py` recria o banco padrão e cadastra tutores, animais, serviços e um agendamento inicial.

## Interface gráfica

A interface foi construída com Tkinter e `ttk`. Ela possui abas para tutores, animais, serviços, agendamentos e histórico.

As telas de animais e serviços possuem campos dinâmicos conforme a espécie ou tipo selecionado. Exames e cirurgias não têm campos extras. A tela de agendamento permite selecionar um animal, múltiplos serviços, data e hora, além de exibir uma prévia do término estimado e do valor total.

## Decisões de escopo

- A regra de recurso compartilhado foi limitada a consultas com o mesmo veterinário. Talvez hajam duas ou mais salas de consulta e cirurgia, quem sabe?
- Endereço foi mantido como texto simples.
