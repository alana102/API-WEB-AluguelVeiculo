from beanie import Document, Link
from pydantic import BaseModel
from datetime import datetime
from app.modelos.cliente import Cliente
from app.modelos.veiculo import Veiculo

class Pagamento(BaseModel):
    """
    Representa o registro financeiro de um contrato de locação concluído.

    Relacionamentos:
    - Aluguel: Entidade transacional que contém este registro (Embedded).
    """
    valor_total: float
    metodo: str
    data_pagamento: datetime

class Aluguel(Document):
    """
    Representa o contrato de locação firmado entre um Cliente e um Veículo.

    Relacionamentos:
    - Cliente: Parte que realizou a locação (N:1).
    - Veículo: Objeto da locação (N:1).
    - Pagamento: Registro financeiro embutido (Embedded).
    """
    cliente: Link[Cliente]
    veiculo: Link[Veiculo]
    data_inicio: datetime
    data_fim: datetime
    status: str = "Em andamento"
    pagamento: Pagamento | None

    class Settings:
        name = "alugueis"