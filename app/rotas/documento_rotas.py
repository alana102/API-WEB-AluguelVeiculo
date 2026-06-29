import io
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from miniopy_async.error import S3Error

from app.config.settings import settings
from app.config.minio_client import minio_client
from app.modelos.documento import DocumentoModel

rotas = APIRouter(prefix="/documents", tags=["Documents"])

@rotas.get("/{document_id}", response_model=DocumentoModel)
async def get_documento_metadata(document_id: str):
    """Retorna os metadados do documento armazenados no MongoDB."""
    document = await DocumentoModel.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return document

@rotas.get("/{document_id}/download")
async def download_documento(document_id: str):
    """Baixa ou exibe o arquivo físico armazenado no MinIO."""
    document = await DocumentoModel.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Metadados não encontrados.")

    physical_filename = f"{str(document.id)}.{document.extension}" if document.extension else str(document.id)

    try:
        response = await minio_client.get_object(settings.MINIO_BUCKET_NAME, physical_filename)
        
        file_data = await response.read() 
        
        return StreamingResponse(
            io.BytesIO(file_data), 
            media_type=document.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{document.original_filename}"',
                "Content-Length": str(len(file_data)),  # 🔥 O segredo para o Swagger baixar direto
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except S3Error:
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado no MinIO.")
    finally:
        if 'response' in locals():
            response.close()

@rotas.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_documento(document_id: str):
    """Remove o documento do MongoDB e o arquivo físico do MinIO."""
    document = await DocumentoModel.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    physical_filename = f"{str(document.id)}.{document.extension}" if document.extension else str(document.id)

    try:
        await minio_client.remove_object(settings.MINIO_BUCKET_NAME, physical_filename)
    except S3Error:
        print("Aviso: Arquivo físico já não existia no MinIO.")

    await document.delete()
    return None