from beanie import Document, Link
from pydantic import BaseModel
from datetime import datetime
from app.modelos.cliente import Cliente
from app.modelos.veiculo import Veiculo

class Pagamento(BaseModel):
    valor_total: float
    metodo: str
    data_pagamento: datetime

class Aluguel(Document):
    cliente: Link[Cliente]
    veiculo: Link[Veiculo]
    data_inicio: datetime
    data_fim: datetime
    status: str = "Em andamento"
    pagamento: Pagamento

    class Settings:
        name = "alugueis"