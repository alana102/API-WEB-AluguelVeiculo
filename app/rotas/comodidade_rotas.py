from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from beanie import PydanticObjectId

from app.modelos.comodidade import Comodidade
from app.modelos.veiculo import Veiculo
from app.esquemas.comodidade_DTO import CriarComodidade, AtualizarComodidade, AssociarComodidade

router = APIRouter(prefix="/comodidades", tags=["Comodidades"])


@router.post("/", response_model=Comodidade, status_code=status.HTTP_201_CREATED)
async def criar_comodidade(comodidade_in: CriarComodidade):
    """Cadastra uma nova comodidade (ex.: Ar-condicionado, GPS) que poderá ser associada a veículos."""
    nova_comodidade = Comodidade(**comodidade_in.model_dump())
    await nova_comodidade.insert()
    return nova_comodidade


@router.put("/{id}", response_model=Comodidade)
async def atualizar_comodidade(id: PydanticObjectId, comodidade_atualizada: AtualizarComodidade):
    """Atualiza o nome e/ou a descrição de uma comodidade existente."""
    comodidade = await Comodidade.get(id)
    if not comodidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comodidade não encontrada."
        )

    if comodidade_atualizada.nome is not None:
        comodidade.nome = comodidade_atualizada.nome

    if comodidade_atualizada.descricao is not None:
        comodidade.descricao = comodidade_atualizada.descricao

    await comodidade.save()
    return comodidade


@router.delete("/{id}")
async def deletar_comodidade(id: PydanticObjectId):
    """
    Remove uma comodidade do catálogo.
    Observação: os veículos que referenciavam essa comodidade mantêm o Link apontando
    para um documento inexistente; recomenda-se remover a associação nos veículos antes
    de excluir a comodidade em definitivo.
    """
    comodidade = await Comodidade.get(id)
    if not comodidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comodidade não encontrada."
        )

    await comodidade.delete()
    return {"message": "Comodidade deletada"}


@router.get("/{id}", response_model=Comodidade)
async def buscar_comodidade(id: PydanticObjectId):
    """Busca os detalhes de uma comodidade pelo ID."""
    comodidade = await Comodidade.get(id)
    if not comodidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comodidade não encontrada."
        )
    return comodidade


@router.get("/", response_model=Page[Comodidade])
async def listar_comodidades():
    """Lista todas as comodidades cadastradas, de forma paginada."""
    return await apaginate(Comodidade.find_all())


# --- Associação N:N entre Veiculo e Comodidade ---

@router.post("/veiculos/{id_veiculo}", response_model=Veiculo)
async def associar_comodidade_ao_veiculo(id_veiculo: PydanticObjectId, dados: AssociarComodidade):
    """Associa uma comodidade existente a um veículo (relação N:N)."""
    veiculo = await Veiculo.get(id_veiculo)
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado."
        )

    comodidade = await Comodidade.get(dados.id_comodidade)
    if not comodidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comodidade não encontrada."
        )

    ja_associada = any(c.id == comodidade.id for c in veiculo.comodidades)
    if ja_associada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta comodidade já está associada a este veículo."
        )

    veiculo.comodidades.append(comodidade)
    await veiculo.save()
    return veiculo


@router.delete("/veiculos/{id_veiculo}/{id_comodidade}", response_model=Veiculo)
async def remover_comodidade_do_veiculo(id_veiculo: PydanticObjectId, id_comodidade: PydanticObjectId):
    """Remove a associação entre um veículo e uma comodidade (relação N:N)."""
    veiculo = await Veiculo.get(id_veiculo)
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado."
        )

    nova_lista = [c for c in veiculo.comodidades if c.id != id_comodidade]
    if len(nova_lista) == len(veiculo.comodidades):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esta comodidade não está associada a este veículo."
        )

    veiculo.comodidades = nova_lista
    await veiculo.save()
    return veiculo