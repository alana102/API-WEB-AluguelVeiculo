from beanie import Document

class Ofertador(Document):
    nome: str
    CNPJ: str
    endereco: str
    status: str = "Ativo"

    class Settings:
        name = "ofertador"