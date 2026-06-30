from beanie import Document

class Cliente(Document):
    """
    Representa o usuário final cadastrado na plataforma para realizar locações.

    Relacionamentos:
    - Aluguéis: Histórico de contratos realizados por este cliente (1:N).
    """
    nome: str
    CPF: str
    telefone: str
    status: str = "Ativo"

    class Settings:
        name = "cliente"