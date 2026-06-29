from datetime import datetime, timezone
from beanie import Document as BeanieDocument
from beanie import Link
from pydantic import Field

from app.modelos.veiculo import Veiculo

class DocumentoModel(BeanieDocument):
    original_filename: str = Field(..., description="Nome original do ficheiro enviado")
    content_type: str = Field(..., description="MIME type do ficheiro (ex: application/pdf)")
    extension: str = Field(..., description="Extensão do arquivo")
    size_bytes: int = Field(..., description="Tamanho do ficheiro em bytes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Data e hora do envio")
    veiculo: Link[Veiculo] = Field(..., description="Veículo ao qual este documento pertence")

    class Settings:
        name = "documentos"

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Relatório de Persistência NoSQL",
                "metadata": {
                    "original_name": "trabalho_final.pdf",
                    "content_type": "application/pdf",
                    "extension": "pdf",
                    "size_bytes": 1048576,
                }
            }
        }