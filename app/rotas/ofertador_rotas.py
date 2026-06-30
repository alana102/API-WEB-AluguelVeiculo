from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from beanie import PydanticObjectId

from app.modelos.ofertador import Ofertador
from app.esquemas.ofertador_DTO import CriarOfertador, AtualizarOfertador

router = APIRouter(prefix="/ofertadores", tags=["Ofertadores"])

@router.post("/", response_model=Ofertador, status_code=status.HTTP_201_CREATED)
async def criar_ofertador(ofertador_in: CriarOfertador):
    """
    Cadastra um novo ofertador (empresa ou parceiro) na plataforma.

    Retorna:
    - O objeto do ofertador recém-criado com seu respectivo ID.
    """
    novo_ofertador = Ofertador(
        **ofertador_in.model_dump()
    )
    
    await novo_ofertador.insert()
    return novo_ofertador

@router.put("/{id}", response_model=Ofertador)
async def atualizar_ofertador(id: PydanticObjectId, ofertador_atualizado: AtualizarOfertador):
    """
    Atualiza os dados cadastrais de um ofertador existente.

    Efeitos:
    - Modifica campos como nome, endereço ou status conforme o schema fornecido.
      
    Erros:
    - 404: Caso o ID do ofertador não seja encontrado.
    """
    ofertador = await Ofertador.get(id)
    if not ofertador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ofertador não encontrado."
        )

    if ofertador_atualizado.nome is not None:
        ofertador.nome = ofertador_atualizado.nome
        
    if ofertador_atualizado.endereco is not None:
        ofertador.endereco = ofertador_atualizado.endereco
        
    if ofertador_atualizado.status is not None:
        ofertador.status = ofertador_atualizado.status

    await ofertador.save()
    return ofertador

@router.delete("/{id}")
async def deletar_ofertador(id: PydanticObjectId):
    """
    Remove permanentemente um registro de ofertador do sistema.

    Nota: A operação falhará caso o ofertador possua veículos ativos vinculados.
    
    Erros:
    - 404: Caso o ofertador não seja encontrado.
    """
    ofertador = await Ofertador.get(id)
    if not ofertador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ofertador não encontrado."
        )
        
    await ofertador.delete()
    return {"message":"Ofertador deletado"}

@router.get("/{id}", response_model=Ofertador)
async def buscar_ofertador(id: PydanticObjectId):
    """
    Recupera os detalhes de um ofertador específico por ID.

    Erros:
    - 404: Caso o ID não exista.
    """
    ofertador = await Ofertador.get(id)
    if not ofertador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ofertador não encontrado."
        )
    return ofertador

@router.get("/", response_model=Page[Ofertador])
async def listar_ofertadores():
    """
    Lista todos os ofertadores cadastrados com suporte a paginação.

    Retorna:
    - Uma página contendo a lista de ofertadores.
    """
    return await apaginate(Ofertador.find_all())