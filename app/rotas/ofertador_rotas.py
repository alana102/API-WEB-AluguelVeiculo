from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from beanie import PydanticObjectId

from app.modelos.ofertador import Ofertador
from app.esquemas.ofertador_DTO import CriarOfertador, AtualizarOfertador

router = APIRouter(prefix="/ofertadores", tags=["Ofertadores"])

@router.post("/", response_model=Ofertador, status_code=status.HTTP_201_CREATED)
async def criar_ofertador(ofertador_in: CriarOfertador):
    novo_ofertador = Ofertador(
        **ofertador_in.model_dump()
    )
    
    await novo_ofertador.insert()
    return novo_ofertador

@router.put("/{id}", response_model=Ofertador)
async def atualizar_ofertador(id: PydanticObjectId, ofertador_atualizado: AtualizarOfertador):
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
    ofertador = await Ofertador.get(id)
    if not ofertador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ofertador não encontrado."
        )
    return ofertador

@router.get("/", response_model=Page[Ofertador])
async def listar_ofertadores():
    return await apaginate(Ofertador.find_all())