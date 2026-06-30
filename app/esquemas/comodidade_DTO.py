from pydantic import BaseModel, Field
from beanie import PydanticObjectId


class CriarComodidade(BaseModel):
    """
    Schema utilizado para a criação de um novo registro de Comodidade.

    Campos principais:
    - Todos os atributos obrigatórios definidos no modelo, exceto o ID, 
      que é gerado automaticamente pelo banco de dados.
    """
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
    """
    Schema utilizado para a atualização parcial dos dados de uma comodidade.

    Campos principais:
    - nome, descricao: Campos opcionais. Permite ajustar detalhes do item
      sem a necessidade de sobrescrever todas as informações registradas.
    """
    nome: str | None = Field(None, description="Novo nome da comodidade")
    descricao: str | None = Field(None, description="Nova descrição da comodidade")


class AssociarComodidade(BaseModel):
    """
    Schema utilizado para a associação ou desassociação de comodidades em veículos.

    Campos principais:
    - id_comodidade: Identificador único da comodidade que será vinculada
      ou removida do veículo em questão.
    """
    id_comodidade: PydanticObjectId = Field(..., description="ID da comodidade a ser associada/removida do veículo")

    class Config:
        json_schema_extra = {
            "example": {
                "id_comodidade": "64b1f4b8f3a3d5e2c1d3e4f7"
            }
        }