from beanie import Document, Link
from pydantic import BaseModel, Field
from datetime import datetime

#ESQUEMAS
class Pagamento(BaseModel):
    valor_total: float
    metodo: str
    data_pagamento: datetime

#ENTIDADES
class Ofertador(Document):
    nome: str
    CNPJ: str
    endereco: str
    status: str = "Ativo"

    class Settings:
        name = "ofertador"


class Veiculo(Document):
    placa: str
    tipo: str
    modelo: str
    status: str = "Disponível"
    ofertador: Link[Ofertador]

    class Settings:
        name = "veiculos"

class Cliente(Document):
    nome: str
    CPF: str
    telefone: str
    status: str = "Ativo"

    class Settings:
        name = "cliente"

class Aluguel(Document):
    cliente: Link[Cliente]
    veiculo: Link[Veiculo]
    data_inicio: datetime
    data_fim: datetime
    status: str = "Em andamento"
    pagamento: Pagamento

    class Settings:
        name = "alugueis"

class Documento(Document):
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    created_at: datetime
    veiculo: Link[Veiculo]

    class Settings:
        name = "documentos"
