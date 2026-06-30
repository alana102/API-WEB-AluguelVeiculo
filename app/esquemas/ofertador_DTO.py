from pydantic import BaseModel, Field

class CriarOfertador(BaseModel):
    """
    Schema utilizado para a criação de um novo registro de Ofertador.

    Campos principais:
    - Todos os atributos obrigatórios definidos no modelo, exceto o ID, 
      que é gerado automaticamente pelo banco de dados.
    """
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
    """
    Schema utilizado para a atualização parcial dos dados de um ofertador.

    Campos principais:
    - nome, endereco, status: Campos opcionais. Permite ajustar o cadastro
      sem a necessidade de reenviar todos os dados originais.
    """
    nome: str | None = Field(None, description="Novo nome da empresa")
    endereco: str | None = Field(None, description="Novo endereço do ofertador")
    status: str | None = Field(None, description="Ativo ou Inativo")