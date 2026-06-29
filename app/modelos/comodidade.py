from beanie import Document
from pydantic import Field


class Comodidade(Document):
    """
    Representa um acessório/equipamento que um veículo pode oferecer
    (ex.: Ar-condicionado, GPS, Bancos de couro, Cadeirinha infantil).

    Relacionamento: N:N com Veiculo. Uma Comodidade pode estar presente
    em vários veículos, e um veículo pode ter várias comodidades
    (ver campo `comodidades: list[Link[Comodidade]]` em Veiculo).
    """

    nome: str = Field(..., description="Nome da comodidade (ex.: 'Ar-condicionado')")
    descricao: str | None = Field(None, description="Detalhes adicionais sobre a comodidade")

    class Settings:
        name = "comodidades"

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Ar-condicionado",
                "descricao": "Climatização automática de duas zonas",
            }
        }