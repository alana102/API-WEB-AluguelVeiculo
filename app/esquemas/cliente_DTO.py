from pydantic import BaseModel, Field

class CriarCliente(BaseModel):
    """
    Schema utilizado para a criação de um novo registro de Cliente.

    Campos principais:
    - Todos os atributos obrigatórios definidos no modelo, exceto o ID, 
      que é gerado automaticamente pelo banco de dados.
    """
    nome: str = Field(..., description="Nome completo do cliente")
    CPF: str = Field(..., min_length=11, max_length=14, description="CPF do cliente (apenas número ou formatado)")
    telefone: str = Field(..., description="Telefone de contato com DDD")

    class Config:
        json_schema_extra = {
            "example":{
                "nome":"João de Sousa",
                "CPF":"123.456.789-10",
                "telefone":"99877777777"
            }
        }

class AtualizarCliente(BaseModel):
    """
    Schema utilizado para a atualização parcial dos dados de um cliente.

    Campos principais:
    - nome, telefone, status: Campos opcionais. Se enviados, sobrescrevem
      o valor atual no banco de dados.
    """
    nome: str | None = Field(None, description="Novo nome")
    telefone: str | None = Field(None, description="Novo telefone")
    status: str | None = Field(None, description="Ativo ou Inativo")