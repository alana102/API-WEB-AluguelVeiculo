from beanie import Document, Link
from app.modelos.ofertador import Ofertador
from app.modelos.comodidade import Comodidade

class Veiculo(Document):
    placa: str
    tipo: str
    modelo: str
    status: str = "Disponível"
    ofertador: Link[Ofertador]
    comodidades: list[Link[Comodidade]] = []

    class Settings:
        name = "veiculos"