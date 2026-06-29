from pydantic import BaseModel, Field

class CriarOfertador(BaseModel):
    nome: str = Field(..., description="Nome da empresa ou pessoa física ofertante")
    CNPJ: str = Field(..., description="CNPJ válido da empresa")
    endereco: str = Field(..., description="Endereço físico principal")

    class Config:
        json_schema_extra = {
            "example":{
            "nome":"Locadora X",
            "CNPJ":"12.345.678/0001-99",
            "endereco":"Rua XXXXX, 1111 - Centro"
            }
        }

class AtualizarOfertador(BaseModel):
    nome: str | None = Field(None, description="Novo nome da empresa")
    endereco: str | None = Field(None, description="Novo endereço do ofertador")
    status: str | None = Field(None, description="Ativo ou Inativo")