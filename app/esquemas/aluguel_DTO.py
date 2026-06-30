from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from datetime import datetime

class CriarAluguel(BaseModel):
    """
    Schema utilizado para a requisição de criação de um novo contrato de locação.

    Campos principais:
    - id_cliente: Referência única para o cliente locatário.
    - id_veiculo: Referência única para o veículo a ser alugado.
    - data_inicio/fim: Período solicitado para a vigência do contrato.
    """
    id_cliente: PydanticObjectId = Field(..., description="ID do Cliente no banco de dados")
    id_veiculo: PydanticObjectId = Field(..., description="ID do veículo desejado")
    data_inicio: datetime = Field(..., description="Data e hora de retirada do veículo")
    data_fim: datetime = Field(..., description="Data e hora presvista para devolução")

    class Config:
        json_schema_extra = {
            "example":{
                "id_cliente":"64b1f4b8f3a3d5e2c1d3e4f5",
                "id_veiculo":"64b1f4b8f3a3d5e2c1d3e4f6",
                "data_inicio":"2026-07-01T10:00:00Z",
                "data_fim": "2026-07-05T10:00:00Z"
            }
        }

class AtualizarAluguel(BaseModel):
    """
    Schema utilizado para a atualização parcial de um contrato de locação.

    Campos principais:
    - data_fim: Permite estender ou reduzir a duração do aluguel.
    - status: Permite alterar o estado do contrato (ex: concluído, cancelado).
    """
    data_fim: datetime | None = None
    status: str | None = Field(None, description="Em andamento, Concluído, Cancelado")

class CriarPagamento(BaseModel):
    """
    Schema utilizado para o processamento do pagamento de um aluguel.

    Campos principais:
    - valor_total: O montante final a ser pago.
    - metodo: Forma de pagamento utilizada (ex: cartão, pix, boleto).
    """
    metodo: str = Field(..., description="Método de pagamento (ex.: Pix, Cartão de Crédito)")
    valor_total: float = Field(..., description="Valor cobrado pelo aluguel", gt=0)
    class Config:
        json_schema_extra = {
            "example":{
                "metodo":"Pix",
                "valor_total":250.0
            }
        }