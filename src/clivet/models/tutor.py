from dataclasses import dataclass

from clivet.errors import UnprocessableEntityError


@dataclass
class Tutor:
    cpf: str
    name: str
    phone: str
    email: str
    address: str

    def __post_init__(self) -> None:
        self.cpf = self.cpf.strip()
        self.name = self.name.strip()
        self.phone = self.phone.strip()
        self.email = self.email.strip()
        self.address = self.address.strip()
        if not self.cpf or not self.name or not self.phone or not self.email or not self.address:
            raise UnprocessableEntityError("CPF, nome, telefone, e-mail e endereço do tutor são obrigatórios.")
