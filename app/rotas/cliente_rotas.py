from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from beanie import PydanticObjectId

from app.modelos.cliente import Cliente
from app.esquemas.cliente_DTO import CriarCliente, AtualizarCliente

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
async def criar_cliente(cliente_in: CriarCliente):
    novo_cliente = Cliente(
        **cliente_in.model_dump()
    )

    await novo_cliente.insert()
    return novo_cliente

@router.put("/{id}", response_model=Cliente)
async def atualizar_cliente(id: PydanticObjectId, cliente_atualizado: AtualizarCliente):
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    if cliente_atualizado is not None:
        cliente.nome = cliente_atualizado.nome

    if cliente_atualizado.telefone is not None:
        cliente.telefone = cliente_atualizado.telefone
        
    if cliente_atualizado.status is not None:
        cliente.status = cliente_atualizado.status

    await cliente.save()
    return cliente

@router.delete("/{id}")
async def deletar_cliente(id: PydanticObjectId):
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cliente não encontrado."
        )
        
    await cliente.delete()
    return {"message":"Cliente deletado"}

@router.get("/{id}", response_model=Cliente)
async def buscar_cliente(id: PydanticObjectId):
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cliente não encontrado."
        )
    return cliente

@router.get("/", response_model=Page[Cliente])
async def listar_clientes():
    return await apaginate(Cliente.find_all())