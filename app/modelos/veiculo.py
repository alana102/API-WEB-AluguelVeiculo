from beanie import Document, Link
from app.modelos.ofertador import Ofertador
from app.modelos.comodidade import Comodidade

class Veiculo(Document):
    """
    Representa o ativo principal disponível para locação no sistema.

    Relacionamentos:
    - Ofertador: Proprietário responsável pelo veículo (N:1).
    - Comodidades: Itens ou acessórios inclusos no veículo (N:N).
    - Aluguéis: Histórico de contratos vinculados a este veículo (1:N).
    - Documentos: Arquivos e imagens associados ao veículo (1:N).
    """
    placa: str
    tipo: str
    modelo: str
    status: str = "Disponível"
    ofertador: Link[Ofertador]
    comodidades: list[Link[Comodidade]] = []

    class Settings:
        name = "veiculos"