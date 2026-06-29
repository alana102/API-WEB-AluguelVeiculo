from beanie import Document

class Cliente(Document):
    nome: str
    CPF: str
    telefone: str
    status: str = "Ativo"

    class Settings:
        name = "cliente"