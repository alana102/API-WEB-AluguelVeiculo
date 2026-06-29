from beanie import Document, Link
from app.modelos.ofertador import Ofertador

class Veiculo(Document):
    placa: str
    tipo: str
    modelo: str
    status: str = "Disponível"
    ofertador: Link[Ofertador]

    class Settings:
        name = "veiculos"