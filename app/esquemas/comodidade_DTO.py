from pydantic import BaseModel, Field
from beanie import PydanticObjectId


class CriarComodidade(BaseModel):
    nome: str = Field(..., description="Nome da comodidade (ex.: 'GPS')")
    descricao: str | None = Field(None, description="Detalhes adicionais sobre a comodidade")

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "GPS",
                "descricao": "Sistema de navegação integrado",
            }
        }


class AtualizarComodidade(BaseModel):
    nome: str | None = Field(None, description="Novo nome da comodidade")
    descricao: str | None = Field(None, description="Nova descrição da comodidade")


class AssociarComodidade(BaseModel):
    id_comodidade: PydanticObjectId = Field(..., description="ID da comodidade a ser associada/removida do veículo")

    class Config:
        json_schema_extra = {
            "example": {
                "id_comodidade": "64b1f4b8f3a3d5e2c1d3e4f7"
            }
        }