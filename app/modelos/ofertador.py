from beanie import Document

class Ofertador(Document):
    """
    Representa o fornecedor ou proprietário que disponibiliza veículos.

    Relacionamentos:
    - Veículos: Lista de automóveis vinculados a este ofertador (1:N).
    """
    nome: str
    CNPJ: str
    endereco: str
    status: str = "Ativo"

    class Settings:
        name = "ofertador"