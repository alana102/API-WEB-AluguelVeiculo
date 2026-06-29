from pydantic import BaseModel, Field
from beanie import PydanticObjectId

class CriarVeiculo(BaseModel):
    placa: str = Field(..., min_length=7, max_length=8, description="Placa do veículo (ex.:ABC-1234 ou ABC12345)")
    tipo: str = Field(..., description="Categoria do veículo (ex.: SUV, Hatches, Sedan)")
    modelo: str = Field(..., description="Nome do modelo (ex.: Honda Civic)")
    id_ofertador: PydanticObjectId = Field(..., description="ID do fornecedor que está cadastrando o veículo")

    class Config:
        json_schema_extra = {
            "example":{
                "placa":"ABC-1234",
                "tipo":"Sedan",
                "modelo":"Honda Civic",
                "id_ofertador":"64b1f4b8f3a3d5e2c1d3e4f5"
            }
        }
class AtualizarVeiculo(BaseModel):
    placa: str | None = Field(None, description="Nova Placa")
    tipo: str | None = Field(None, description="Tipo modificado")
    modelo: str | None = Field(None, description="Modelo modificado")
    status: str | None = Field(None, description="Disponível, Alugado ou Em Manutenção")