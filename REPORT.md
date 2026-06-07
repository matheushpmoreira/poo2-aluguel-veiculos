# Relatório do Projeto

Este projeto implementa um sistema para gerenciamento de aluguel de veículos, usando Python, Tkinter e SQLite.

A aplicação foi organizada em dois módulos principais: `backend`, responsável pelas regras de negócio e persistência, e `frontend`, responsável pela interface gráfica. O módulo `backend` possui arquitetura similar à arquitetura em camadas, utilizada no desenvolvimento de backends para a web.

O sistema permite cadastrar, listar, atualizar e remover veículos e clientes, criar e finalizar aluguéis, realizar login de cliente no painel público e consultar veículos disponíveis para aluguel.

## Classes

### Modelos

- `Vehicle`: representa um veículo cadastrado, com placa, marca, modelo, ano, tipo, valor da diária e status.
- `Customer`: representa um cliente, com código ou CPF, nome, telefone, e-mail, endereço e senha.
- `Rental`: representa um aluguel, com cliente, veículo, datas, quantidade de dias, valor total e status.
- `VehicleStatus`, `VehicleType` e `RentalStatus`: enums de *string* que representam o estado de um veículo (disponível ou alugado), o tipo de veículo (carro, moto, etc.) e o estado de um aluguel (ativo ou concluído).

### Camada de repositórios

- `Database`: encapsula a conexão com SQLite e cria as tabelas necessárias.
- `VehicleRepository`: realiza operações de banco relacionadas a veículos.
- `CustomerRepository`: realiza operações de banco relacionadas a clientes.
- `RentalRepository`: realiza operações de banco relacionadas a aluguéis.

### Camada de serviço

- `VehicleService`: concentra as regras de cadastro, alteração, remoção, busca e validação de veículos.
- `CustomerService`: concentra as regras de cadastro, alteração, remoção, busca e login de clientes.
- `RentalService`: concentra as regras de criação, finalização, listagem e cálculo de multa de aluguéis.

### Camada de controle

- `AppController`: fornece métodos de alto nível, nomeados conforme operações HTTP, como `post_vehicle`, `get_vehicles`, `put_vehicle`, `post_rental` e `post_customer_login`. Essa classe desacopla a interface gráfica dos serviços internos.
- `BackendError` e suas subclasses: representam erros do backend com códigos de HTTP, como `400`, `401`, `404`, `409` e `422`.

### Interface gráfica

- `RentalSystemApp`: janela principal da aplicação.
- `AdminPanel`: painel administrativo com abas para veículos, clientes, aluguéis e relatórios.
- `VehicleAdminFrame`, `CustomerAdminFrame` e `RentalAdminFrame`: telas administrativas para operar sobre cada entidade.
- `PublicPanel`: área pública para login do cliente, visualização de veículos disponíveis e criação de aluguel.
- `BaseFrame`, `Action`, `Choice`, `ChoiceBox`, `Column` e `DataTable`: classes auxiliares para mensagens, botões, opções tipadas e tabelas reutilizáveis.

## Conceitos de POO utilizados

### Classes e objetos

As entidades principais do sistema foram modeladas como classes. Durante a execução, objetos de `Vehicle`, `Customer` e `Rental` representam os dados manipulados pelo sistema.

### Atributos e métodos

As classes possuem atributos próprios e métodos relacionados ao seu comportamento. Por exemplo, `Vehicle` possui `set_rented`, `set_available` e `calc_rental_cost`, enquanto `Rental` possui o método de fábrica `create` e o método `set_finished`.

### Encapsulamento

A lógica de negócio não fica misturada com a interface gráfica. O frontend invoca apenas ao `AppController`, enquanto regras como disponibilidade de veículo, cálculo de valor total, login e finalização de aluguel ficam nos serviços e modelos.

### Herança

A interface gráfica usa herança com `BaseFrame`, que centraliza o acesso ao controller e os métodos comuns de exibição de mensagens. Os painéis específicos herdam esse comportamento e adicionam suas próprias telas.

### Polimorfismo

Na interface gráfica, os widgets auxiliares usam tipos genéricos para trabalhar com diferentes objetos de domínio sem duplicar a lógica.

### Composição

O controller compõe serviços, os serviços compõem repositórios e os repositórios compõem a conexão com o banco. Na interface, os painéis compõem tabelas, campos, botões e caixas de seleção.

## Regras de negócio implementadas

- Um veículo alugado não pode ser alugado novamente.
- Um aluguel só pode ser criado para um cliente cadastrado.
- Um aluguel só pode ser criado para um veículo cadastrado.
- Um aluguel só pode ser criado se o veículo estiver disponível.
- Ao criar um aluguel, o veículo passa para o status `rented`.
- Ao finalizar um aluguel, o veículo volta para o status `available`.
- O valor total do aluguel é calculado automaticamente com base no valor da diária e na quantidade de dias.
- Campos obrigatórios de veículos, clientes e aluguéis são validados.
- Status de veículos e aluguéis usam enums, evitando valores livres inválidos.
- O login de cliente compara o código e a senha cadastrada.
- Erros do backend usam classes específicas com códigos inspirados em HTTP.
- A multa por atraso é calculada para aluguéis ativos após a data prevista de devolução.

## Persistência de dados

O sistema usa SQLite para persistência. A classe `Database` cria automaticamente as tabelas de veículos, clientes e aluguéis. Os repositórios fazem a tradução entre linhas do banco e objetos do domínio.

Também foi criado um script de população em `scripts/seed_database.py`, executável pelo comando configurado em `pyproject.toml`. Esse script recria o banco padrão e cadastra veículos, clientes e um aluguel inicial.

## Interface gráfica

A interface foi construída com Tkinter e `ttk`. Ela possui uma janela principal com abas, separando o painel administrativo da área pública.

No painel administrativo, o usuário pode gerenciar veículos, clientes e aluguéis. Na área pública, o cliente pode fazer login, visualizar veículos disponíveis e criar um aluguel usando sua própria conta.

Os textos apresentados ao usuário estão em português. Internamente, o sistema mantém valores em inglês para enums e dados de domínio, evitando que a lógica dependa dos rótulos exibidos na tela.

## Melhorias futuras

- Finalizar a tela de relatórios administrativos com listagens e exportação.
- Melhorar o modelo da interface, com classes reutilizáveis para formulários e inputs.
- Adicionar um formulário de busca mais avançado.
- Adicionar confirmação antes de operações destrutivas.
