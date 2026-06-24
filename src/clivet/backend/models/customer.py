from dataclasses import dataclass

from clivet.backend.errors import UnprocessableEntityError


@dataclass
class Customer:
    code: str
    name: str
    phone: str
    email: str
    address: str
    password: str

    def __post_init__(self) -> None:
        self.code = self.code.strip()
        self.name = self.name.strip()
        self.phone = self.phone.strip()
        self.email = self.email.strip()
        self.address = self.address.strip()
        self.password = self.password.strip()

        if not all([self.code, self.name, self.phone, self.email, self.address, self.password]):
            raise UnprocessableEntityError("Todos os campos do cliente são obrigatórios.")

    def check_password(self, password: str) -> bool:
        return self.password == password
