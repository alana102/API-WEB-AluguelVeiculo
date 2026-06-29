from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from beanie import PydanticObjectId
from datetime import datetime, timezone

from app.modelos.aluguel import Aluguel, Pagamento
from app.esquemas.aluguel_DTO import CriarAluguel, AtualizarAluguel, CriarPagamento
from app.modelos.cliente import Cliente
from app.modelos.veiculo import Veiculo

router = APIRouter(prefix="/alugueis", tags=["Alugueis"])

@router.post("/", response_model=Aluguel, status_code=status.HTTP_201_CREATED)
async def criar_aluguel(aluguel_in: CriarAluguel):
    cliente = await Cliente.get(aluguel_in.id_cliente)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    if cliente.status != "Ativo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente inativo."
        )
    veiculo = await Veiculo.get(aluguel_in.id_veiculo)
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado."
        )
    if veiculo.status != "Disponível":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este veículo não está disponível para aluguel no momento."
        )
    
    novo_aluguel = Aluguel(
        **aluguel_in.model_dump(exclude={"id_cliente", "id_veiculo"}),
        cliente=cliente,
        veiculo=veiculo,
        status="Em andamento"
    )
    await novo_aluguel.insert()
    veiculo.status = "Alugado"
    await veiculo.save()
    return novo_aluguel

@router.put("/{id}", response_model=Aluguel)
async def atualizar_aluguel(id: PydanticObjectId, aluguel_atualizado: AtualizarAluguel):
    aluguel = await Aluguel.get(id, fetch_links=True)

    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluguel não encontrado"
        )
    status_antigo = aluguel.status

    if aluguel_atualizado.data_fim is not None:
        aluguel.data_fim = aluguel_atualizado.data_fim

    if aluguel_atualizado.status is not None:
        aluguel.status = aluguel_atualizado.status

    if status_antigo == "Em andamento" and aluguel.status in ["Concluído", "Cancelado"]:
        aluguel.veiculo.status = "Disponível"
        await aluguel.veiculo.save()
    
    await aluguel.save()
    return aluguel

@router.post("/{id}/pagar", response_model=Aluguel)
async def pagar_aluguel(id:PydanticObjectId, pagamento_in: CriarPagamento):
    aluguel = await Aluguel.get(id, fetch_links=True)
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluguel não encontrado."
        )
    if aluguel.pagamento is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este aluguel já possui um pagamento registrado."
        )
    
    novo_pagamento = Pagamento(
        **pagamento_in.model_dump(),
        data_pagamento = datetime.now(timezone.utc)
    )
    aluguel.pagamento = novo_pagamento
    aluguel.status = "Concluído"

    aluguel.veiculo.status = "Disponível"
    await aluguel.veiculo.save()

    await aluguel.save()
    return aluguel

@router.delete("/{id}")
async def deletar_aluguel(id: PydanticObjectId):
    aluguel = await Aluguel.get(id)
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluguel não encontrado"
        )
    await aluguel.delete()
    return {"message":"Aluguel deletado"}

@router.get("/{id}", response_model=Aluguel)
async def buscar_aluguel(id: PydanticObjectId):
    aluguel = await Aluguel.get(id, fetch_links=True)
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Aluguel não encontrado."
        )
    return aluguel

@router.get("/", response_model=Page[Aluguel])
async def listar_aluguel():
    return await apaginate(Aluguel.find_all(fetch_links=True))