import io
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from miniopy_async.error import S3Error

from app.config.settings import settings
from app.config.minio_client import minio_client
from app.modelos.documento import DocumentoModel

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.beanie import apaginate as beanie_paginate

rotas = APIRouter(prefix="/documents", tags=["Documents"])

@rotas.get("/{document_id}", response_model=DocumentoModel)
async def get_documento_metadata(document_id: str):
    """Retorna os metadados do documento armazenados no MongoDB."""
    document = await DocumentoModel.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return document

@rotas.get("/", response_model=Page[DocumentoModel])
async def listar_documentos(params: Params = Depends()):
    """
    Retorna uma lista paginada de todos os metadados de documentos no MongoDB.
    Aceita os query params 'page' (padrão 1) e 'size' (padrão 50).
    """
    try:
        return await beanie_paginate(DocumentoModel, params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar documentos: {str(e)}"
        )

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

@rotas.put("/{document_id}", response_model=DocumentoModel)
async def substituir_documento(document_id: str, file: UploadFile = File(...)):
    """
    Substitui o arquivo físico no MinIO e atualiza seus metadados no MongoDB.
    Mantém o mesmo ID do documento.
    """

    document = await DocumentoModel.get(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Documento não encontrado para substituição."
        )
    
    old_extension = document.extension
    old_physical_filename = f"{str(document.id)}.{old_extension}" if old_extension else str(document.id)

    try:
        original_filename = file.filename
        content_type = file.content_type or "application/octet-stream"
        new_extension = original_filename.split(".")[-1] if "." in original_filename else ""
        
        file_content = await file.read()
        size_bytes = len(file_content)

        if new_extension != old_extension:
            try:
                await minio_client.remove_object(settings.MINIO_BUCKET_NAME, old_physical_filename)
            except S3Error:
                print(f"Aviso: Arquivo antigo {old_physical_filename} não foi encontrado no MinIO para remoção.")

        new_physical_filename = f"{str(document.id)}.{new_extension}" if new_extension else str(document.id)
        
        await minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=new_physical_filename,
            data=io.BytesIO(file_content),
            length=size_bytes,
            content_type=content_type
        )

        document.original_filename = original_filename
        document.content_type = content_type
        document.extension = new_extension
        document.size_bytes = size_bytes

        await document.save()  

        return document

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao substituir o documento: {str(e)}"
        )


@rotas.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_documento(document_id: str):
    """Remove o documento do MongoDB e o arquivo físico do MinIO."""
    document = await DocumentoModel.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    physical_filename = f"{str(document.id)}.{document.extension}" if document.extension else str(document.id)

    try:
        await minio_client.remove_object(settings.MINIO_BUCKET_NAME, physical_filename)
    except S3Error:
        print(f"Aviso: Arquivo físico já não existia no MinIO.")

    await document.delete()
    return {
        "status": "sucesso",
        "mensagem": f"Arquivo {document_id} deletado com sucesso!",
        "documento_id": document_id
    }