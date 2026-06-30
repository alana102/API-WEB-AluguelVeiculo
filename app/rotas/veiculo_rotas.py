import io
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.beanie import apaginate
from beanie import PydanticObjectId

from app.modelos.veiculo import Veiculo
from app.modelos.ofertador import Ofertador
from app.modelos.documento import DocumentoModel
from app.esquemas.veiculo_DTO import CriarVeiculo, AtualizarVeiculo
from app.config.settings import settings
from app.config.minio_client import minio_client

router = APIRouter(prefix="/veiculos", tags=["Veiculos"])

@router.post("/", response_model=Veiculo, status_code=status.HTTP_201_CREATED)
async def criar_veiculo(veiculo_in: CriarVeiculo):
    """
    Cadastra um novo veículo vinculado a um ofertador.

    Relacionamentos e Efeitos:
    - Ofertador: Valida se o ofertador existe e se está com status 'Ativo'.
    
    Erros:
    - 404: Se o ofertador informado não existir.
    - 400: Se o ofertador estiver inativo.
    """
    ofertador = await Ofertador.get(veiculo_in.id_ofertador)

    if not ofertador:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Ofertador não encontrado."
        )

    if ofertador.status != "Ativo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ofertador inativo. Não é possível cadastrar veículo."
        )

    novo_veiculo = Veiculo(
        **veiculo_in.model_dump(exclude={"id_ofertador"}),
        ofertador=ofertador
    )

    await novo_veiculo.insert()
    return novo_veiculo

@router.put("/{id}", response_model=Veiculo)
async def atualizar_veiculo(id: PydanticObjectId, veiculo_atualizado: AtualizarVeiculo):
    """
    Atualiza os dados cadastrais de um veículo.

    Efeitos:
    - Modifica campos como placa, modelo, tipo ou status.
    
    Erros:
    - 404: Se o ID do veículo não for encontrado.
    """
    veiculo = await Veiculo.get(id);
    if not veiculo:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado."
        )
    
    if veiculo_atualizado.placa is not None:
        veiculo.placa = veiculo_atualizado.placa

    if veiculo_atualizado.tipo is not None:
        veiculo.tipo = veiculo_atualizado.tipo

    if veiculo_atualizado.modelo is not None:
        veiculo.modelo = veiculo_atualizado.modelo

    if veiculo_atualizado.status is not None:
        veiculo.status = veiculo_atualizado.status

    await veiculo.save()
    return veiculo

@router.delete("/{id}")
async def deletar_veiculo(id: PydanticObjectId):
    """
    Remove um veículo permanentemente do sistema.

    Nota: A operação pode falhar se o veículo estiver vinculado a aluguéis ativos.
    
    Erros:
    - 404: Caso o veículo não seja encontrado.
    """
    veiculo = await Veiculo.get(id)
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Veículo não encontrado."
        )
    
    await veiculo.delete()
    return {"message":"Veículo deletado"}

@router.get("/{id}", response_model=Veiculo)
async def buscar_veiculo(id: str):
    """
    Recupera os detalhes de um veículo específico por ID.

    Erros:
    - 404: Caso o ID não exista.
    """
    veiculo = await Veiculo.get(id)
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Veículo não encontrado."
        )
    return veiculo

@router.get("/", response_model=Page[Veiculo])
async def listar_veiculos(params: Params = Depends()):
    """
    Lista todos os veículos cadastrados com suporte a paginação.

    Retorna:
    - Uma página contendo a lista de veículos.
    """
    try:
        return await apaginate(Veiculo, params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar veículos: {str(e)}"
        )
   # return await apaginate(Veiculo.find_all(fetch_links=True))

@router.post("/{id}/documents", response_model=DocumentoModel, status_code=status.HTTP_201_CREATED)
async def upload_documento_veiculo(id: PydanticObjectId, file: UploadFile = File(...)):
    """
    Faz o upload de um documento para o MinIO e registra seus metadados.

    Fluxo:
    1. Valida existência do veículo.
    2. Persiste metadados (nome, extensão, tamanho) no MongoDB.
    3. Envia o arquivo físico para o bucket do MinIO.
    
    Tratamento de erro:
    - Remove os metadados do MongoDB caso o upload para o MinIO falhe.
    
    Erros:
    - 404: Caso o veículo não seja encontrado.
    - 500: Erro no processamento ou na comunicação com o MinIO.
    """
    veiculo = await Veiculo.get(id)

    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado."
        )
    
    try:
        original_filename = file.filename
        content_type = file.content_type or "application/octet-stream"
        extension = original_filename.split(".")[-1] if "." in original_filename else ""
        
        file_content = await file.read()
        size_bytes = len(file_content)

        document_meta = DocumentoModel(
            original_filename=original_filename,
            content_type=content_type,
            extension=extension,
            size_bytes=size_bytes,
            veiculo=veiculo
        )
        await document_meta.insert()

        physical_filename = f"{str(document_meta.id)}.{extension}" if extension else str(document_meta.id)

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