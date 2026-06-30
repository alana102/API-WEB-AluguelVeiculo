from fastapi import APIRouter, HTTPException, status, Depends
from fastapi_pagination import Page, Params
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
    """
    Registra um novo contrato de locação no sistema.

    Relacionamentos e Efeitos:
    - Cliente: Valida se o cliente está 'Ativo'.
    - Veículo: Valida disponibilidade e altera status para 'Alugado'.
    
    Erros:
    - 404: Caso o cliente ou veículo não existam.
    - 400: Caso o cliente esteja inativo ou o veículo indisponível.
    """
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
        status="Em andamento",
        pagamento=None
    )
    await novo_aluguel.insert()
    veiculo.status = "Alugado"
    await veiculo.save()
    return novo_aluguel

@router.put("/{id}", response_model=Aluguel)
async def atualizar_aluguel(id: PydanticObjectId, aluguel_atualizado: AtualizarAluguel):
    """
    Atualiza dados de um aluguel e gerencia o status do veículo.

    Relacionamentos e Efeitos:
    - Veículo: Se o status mudar para 'Concluído' ou 'Cancelado', 
      o veículo é liberado para 'Disponível'.
      
    Erros:
    - 404: Caso o aluguel não seja encontrado.
    """
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
    """
    Registra o pagamento de um aluguel e finaliza o contrato.

    Relacionamentos e Efeitos:
    - Pagamento: Adiciona o registro financeiro ao documento do aluguel.
    - Veículo: Atualiza status para 'Disponível' automaticamente.
    
    Erros:
    - 400: Caso o aluguel já possua um pagamento registrado.
    - 404: Caso o aluguel não seja encontrado.
    """
    aluguel = await Aluguel.get(id)
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
    veiculo_real = await aluguel.veiculo.fetch()
    aluguel.pagamento = novo_pagamento
    aluguel.status = "Concluído"

    veiculo_real.status = "Disponível"
    await veiculo_real.save()

    await aluguel.save()
    return aluguel

@router.delete("/{id}")
async def deletar_aluguel(id: PydanticObjectId):
    """
    Remove um registro de aluguel e libera o veículo associado.

    Efeitos:
    - Veículo: O veículo vinculado é retornado ao status 'Disponível'.
    
    Erros:
    - 404: Caso o aluguel não seja encontrado.
    """
    aluguel = await Aluguel.get(id)
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluguel não encontrado"
        )
    veiculo_real = await aluguel.veiculo.fetch()
    veiculo_real.status = "Disponível"
    await aluguel.delete()
    return {"message":"Aluguel deletado"}

@router.get("/{id}", response_model=Aluguel)
async def buscar_aluguel(id: PydanticObjectId):
    """
    Retorna os detalhes de um aluguel específico.

    Erros:
    - 404: Caso o ID informado não exista no banco.
    """
    aluguel = await Aluguel.get(id)
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Aluguel não encontrado."
        )
    return aluguel

@router.get("/", response_model=Page[Aluguel])
async def listar_aluguel(params: Params = Depends()):
    """
    Lista todos os aluguéis registrados com suporte a paginação.

    Retorna:
    - Uma página de objetos Aluguel com metadados de paginação.
    """
    try:
        return await apaginate(Aluguel, params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar documentos: {str(e)}"
        )
    # return await apaginate(Aluguel.find_all(fetch_links=True))