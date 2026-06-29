from beanie import Document, Link
from modelos import Ofertador

class Veiculo(Document):
    placa: str
    tipo: str
    modelo: str
    status: str = "Disponível"
    ofertador: Link[Ofertador]

    class Settings:
        name = "veiculos"