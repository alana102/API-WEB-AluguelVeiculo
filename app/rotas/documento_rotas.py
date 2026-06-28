import io
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from miniopy_async.error import S3Error

from app.config.settings import settings
from app.config.minio_client import minio_client
from app.modelos.documento import DocumentoModel

rotas = APIRouter(prefix="/documents", tags=["Documents"])

@rotas.post("/", response_model=DocumentoModel, status_code=status.HTTP_201_CREATED)
async def upload_documento(file: UploadFile = File(...)):
    """Envia um novo arquivo para o MinIO e salva seus metadados no MongoDB."""
    try:
        original_filename = file.filename
        content_type = file.content_type or "application/octet-stream"
        extension = original_filename.split(".")[-1] if "." in original_filename else ""
        
        # Lê o conteúdo para calcular o tamanho real em bytes
        file_content = await file.read()
        size_bytes = len(file_content)

        # 1. Cria primeiro o metadado no MongoDB para obter o ID único
        document_meta = DocumentoModel(
            original_filename=original_filename,
            content_type=content_type,
            extension=extension,
            size_bytes=size_bytes
        )
        await document_meta.insert()

        # 2. Usa o ID gerado pelo MongoDB como o nome físico do arquivo no MinIO
        physical_filename = f"{str(document_meta.id)}.{extension}" if extension else str(document_meta.id)

        # 3. Envia o arquivo físico para o MinIO
        await minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=physical_filename,
            data=io.BytesIO(file_content),
            length=size_bytes,
            content_type=content_type
        )

        return document_meta

    except Exception as e:
        if 'document_meta' in locals() and document_meta.id:
            await document_meta.delete()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )

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