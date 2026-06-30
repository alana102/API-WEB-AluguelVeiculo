"""
Rotas de Consultas Avançadas — Integrante 3
============================================
Cobre todos os requisitos de busca complexa exigidos no trabalho:

1. Listagens filtradas por relacionamentos (veículos de um ofertador, aluguéis de um cliente)
2. Busca por texto parcial e case-insensitive ($regex)
3. Filtros por data/ano ($gte, $lte, $expr, $year)
4. Agregações e contagens (aggregation pipelines com $group, $count, $sum)
5. Classificações e ordenações (sort por campo, direção e limite configuráveis)
6. Consultas complexas envolvendo múltiplas coleções ($lookup + $unwind)
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from beanie import PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.modelos.cliente import Cliente
from app.modelos.ofertador import Ofertador
from app.modelos.veiculo import Veiculo
from app.modelos.aluguel import Aluguel
from app.modelos.documento import DocumentoModel
from app.modelos.comodidade import Comodidade

router = APIRouter(prefix="/consultas", tags=["Consultas Avançadas"])


# ---------------------------------------------------------------------------
# 1. LISTAGENS FILTRADAS POR RELACIONAMENTOS
# ---------------------------------------------------------------------------

@router.get("/veiculos/por-ofertador/{id_ofertador}", response_model=Page[Veiculo], summary="Veículos de um ofertador")
async def veiculos_por_ofertador(id_ofertador: PydanticObjectId):
    """
    Retorna os veículos cadastrados por um ofertador específico, de forma paginada.

    Demonstra **listagem filtrada por relacionamento 1:N** (Ofertador → Veiculo).
    """
    ofertador = await Ofertador.get(id_ofertador)
    if not ofertador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ofertador não encontrado.")

    veiculos = await Veiculo.find(
        Veiculo.ofertador.id == id_ofertador
    ).to_list()

    return {"total": len(veiculos), "veiculos": veiculos}


@router.get("/alugueis/por-cliente/{id_cliente}", response_model=Page[Aluguel], summary="Aluguéis de um cliente")
async def alugueis_por_cliente(id_cliente: PydanticObjectId):
    """
    Retorna os aluguéis associados a um cliente específico, de forma paginada.

    Demonstra **listagem filtrada por relacionamento N:1** (Cliente → Aluguel).
    """
    cliente = await Cliente.get(id_cliente)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")

    alugueis = await Aluguel.find(
        Aluguel.cliente.id == id_cliente
    ).to_list()

    return {"total": len(alugueis), "alugueis": alugueis}


@router.get("/alugueis/por-veiculo/{id_veiculo}", response_model=Page[Aluguel], summary="Aluguéis de um veículo")
async def alugueis_por_veiculo(id_veiculo: PydanticObjectId):
    """
    Retorna os aluguéis de um veículo específico, de forma paginada.

    Demonstra **listagem filtrada por relacionamento N:1** (Veiculo → Aluguel).
    """
    veiculo = await Veiculo.get(id_veiculo)
    if not veiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")

    alugueis = await Aluguel.find(
        Aluguel.veiculo.id == id_veiculo
    ).to_list()

    return {"total": len(alugueis), "alugueis": alugueis}


@router.get("/veiculos/por-comodidade/{id_comodidade}", response_model=Page[Veiculo], summary="Veículos com uma comodidade específica")
async def veiculos_por_comodidade(id_comodidade: PydanticObjectId):
    """
    Retorna os veículos que possuem uma comodidade específica, de forma paginada.

    Demonstra **listagem filtrada pelo relacionamento N:N** (Veiculo ↔ Comodidade).
    """
    comodidade = await Comodidade.get(id_comodidade)
    if not comodidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comodidade não encontrada.")

    veiculos = await Veiculo.find(
        {"comodidades.$id": id_comodidade}
    ).to_list()

    return {"comodidade": comodidade.nome, "total": len(veiculos), "veiculos": veiculos}


# ---------------------------------------------------------------------------
# 2. BUSCA POR TEXTO PARCIAL E CASE-INSENSITIVE ($regex)
# ---------------------------------------------------------------------------

@router.get("/clientes/buscar", response_model=Page[Cliente], summary="Busca de clientes por nome ou CPF")
async def buscar_clientes(
    q: str = Query(..., description="Texto para busca parcial no nome ou CPF do cliente")
):
    """
    Busca clientes cujo **nome** ou **CPF** contenha o texto informado, de forma paginada.

    Demonstra **busca por texto parcial e case-insensitive** usando operador `$regex`
    com a opção `i` (ignore case) do MongoDB.
    """
    filtro = {
        "$or": [
            {"nome": {"$regex": q, "$options": "i"}},
            {"CPF": {"$regex": q, "$options": "i"}},
        ]
    }
    return await apaginate(Cliente.find(filtro))


@router.get("/veiculos/buscar", response_model=Page[Veiculo], summary="Busca de veículos por modelo ou placa")
async def buscar_veiculos(
    q: str = Query(..., description="Texto para busca parcial no modelo ou placa do veículo")
):
    """
    Busca veículos cujo **modelo** ou **placa** contenha o texto informado, de forma paginada.

    Demonstra **busca por texto parcial e case-insensitive** usando `$regex`.
    """
    filtro = {
        "$or": [
            {"modelo": {"$regex": q, "$options": "i"}},
            {"placa": {"$regex": q, "$options": "i"}},
        ]
    }
    veiculos = await Veiculo.find(filtro).to_list()
    return {"total": len(veiculos), "veiculos": veiculos}


@router.get("/ofertadores/buscar", response_model=Page[Ofertador], summary="Busca de ofertadores por nome ou CNPJ")
async def buscar_ofertadores(
    q: str = Query(..., description="Texto para busca parcial no nome ou CNPJ do ofertador")
):
    """
    Busca ofertadores cujo **nome** ou **CNPJ** contenha o texto informado, de forma paginada.

    Demonstra **busca por texto parcial e case-insensitive** usando `$regex`.
    """
    filtro = {
        "$or": [
            {"nome": {"$regex": q, "$options": "i"}},
            {"CNPJ": {"$regex": q, "$options": "i"}},
        ]
    }
    return await apaginate(Ofertador.find(filtro))


# ---------------------------------------------------------------------------
# 3. FILTROS POR DATA/ANO
# ---------------------------------------------------------------------------

@router.get("/alugueis/por-periodo", response_model=Page[Aluguel], summary="Aluguéis em um intervalo de datas")
async def alugueis_por_periodo(
    data_inicio: str = Query(..., description="Data inicial no formato YYYY-MM-DD"),
    data_fim: str = Query(..., description="Data final no formato YYYY-MM-DD"),
):
    """
    Retorna aluguéis cuja `data_inicio` esteja dentro do intervalo informado, de forma paginada.

    Demonstra **filtro por data** usando os operadores `$gte` e `$lte` do MongoDB.
    """
    from datetime import datetime
    try:
        dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD."
        )

    alugueis = await Aluguel.find(
        {"data_inicio": {"$gte": dt_inicio, "$lte": dt_fim}}
    ).to_list()

    return {"total": len(alugueis), "alugueis": alugueis}


@router.get("/alugueis/por-ano/{ano}", response_model=Page[Aluguel], summary="Aluguéis de um ano específico")
async def alugueis_por_ano(ano: int):
    """
    Retorna todos os aluguéis iniciados em um determinado ano, de forma paginada.

    Demonstra **filtro por ano** usando o operador `$expr` combinado com `$year`
    do MongoDB para extrair o ano de um campo datetime.
    """
    alugueis = await Aluguel.find(
        {"$expr": {"$eq": [{"$year": "$data_inicio"}, ano]}}
    ).to_list()

    return {"ano": ano, "total": len(alugueis), "alugueis": alugueis}


# ---------------------------------------------------------------------------
# 4. AGREGAÇÕES E CONTAGENS (aggregation pipelines)
# ---------------------------------------------------------------------------

@router.get("/agregacoes/alugueis-por-status", summary="Contagem de aluguéis agrupados por status")
async def alugueis_por_status():
    """
    Conta quantos aluguéis existem para cada status (ex.: Em andamento, Finalizado, Cancelado).

    Demonstra **aggregation pipeline** com os estágios `$group` e `$sort` do MongoDB.
    """
    collection = Aluguel.get_pymongo_collection()
    pipeline = [
        {"$group": {"_id": "$status", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$project": {"status": "$_id", "total": 1, "_id": 0}},
    ]
    cursor = collection.aggregate(pipeline)
    resultado = []
    async for documento in cursor:
        resultado.append(documento)

    return {"resultado": resultado}


@router.get("/agregacoes/receita-por-metodo-pagamento", summary="Receita total agrupada por método de pagamento")
async def receita_por_metodo_pagamento():
    """
    Soma o `valor_total` dos pagamentos agrupando por `metodo` (ex.: Pix, Cartão, Boleto).

    Demonstra **aggregation pipeline** com `$group` + `$sum` em campo de subdocumento embutido.
    """
    collection = Aluguel.get_pymongo_collection()
    pipeline = [
        {"$group": {
            "_id": "$pagamento.metodo",
            "receita_total": {"$sum": "$pagamento.valor_total"},
            "quantidade": {"$sum": 1},
        }},
        {"$sort": {"receita_total": -1}},
        {"$project": {"metodo": "$_id", "receita_total": 1, "quantidade": 1, "_id": 0}},
    ]
    cursor = collection.aggregate(pipeline)
    resultado = []
    async for documento in cursor:
        resultado.append(documento)
    return {"resultado": resultado}


@router.get("/agregacoes/veiculos-por-tipo", summary="Contagem de veículos agrupados por tipo")
async def veiculos_por_tipo():
    """
    Conta quantos veículos existem para cada tipo (ex.: Carro, Moto, Caminhonete).

    Demonstra **aggregation pipeline** com `$group` + `$count`.
    """
    collection = Veiculo.get_pymongo_collection()
    pipeline = [
        {"$group": {"_id": "$tipo", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$project": {"tipo": "$_id", "total": 1, "_id": 0}},
    ]
    cursor = collection.aggregate(pipeline)
    resultado = []
    async for documento in cursor:
        resultado.append(documento)
    return {"resultado": resultado}


@router.get("/agregacoes/media-valor-aluguel", summary="Valor médio dos aluguéis")
async def media_valor_aluguel():
    """
    Calcula o valor médio, mínimo e máximo dos pagamentos registrados.

    Demonstra **aggregation pipeline** com `$avg`, `$min` e `$max`.
    """
    collection = Aluguel.get_pymongo_collection()
    pipeline = [
        {"$group": {
            "_id": None,
            "media": {"$avg": "$pagamento.valor_total"},
            "minimo": {"$min": "$pagamento.valor_total"},
            "maximo": {"$max": "$pagamento.valor_total"},
            "total_alugueis": {"$sum": 1},
        }},
        {"$project": {"_id": 0, "media": 1, "minimo": 1, "maximo": 1, "total_alugueis": 1}},
    ]
    cursor = collection.aggregate(pipeline)
    resultado = []
    async for documento in cursor:
        resultado.append(documento)
    return resultado[0] if resultado else {}


# ---------------------------------------------------------------------------
# 5. CLASSIFICAÇÕES E ORDENAÇÕES CONFIGURÁVEIS
# ---------------------------------------------------------------------------

CAMPOS_ORDENACAO_VALIDOS = {
    "clientes": ["nome", "status", "CPF"],
    "veiculos": ["modelo", "placa", "tipo", "status"],
    "ofertadores": ["nome", "status", "CNPJ"],
    "alugueis": ["data_inicio", "data_fim", "status", "pagamento.valor_total"],
}


@router.get("/ordenar/clientes", summary="Listar clientes com ordenação configurável")
async def clientes_ordenados(
    campo: str = Query("nome", description="Campo para ordenação: nome, status, CPF"),
    ordem: str = Query("asc", description="Direção: 'asc' para crescente, 'desc' para decrescente"),
    limite: int = Query(20, ge=1, le=100, description="Quantidade máxima de resultados (1-100)"),
):
    """
    Lista clientes com **ordenação configurável** por campo e direção.

    Demonstra uso de **sort dinâmico** no MongoDB com `$sort` configurado via parâmetros de query.
    """
    if campo not in CAMPOS_ORDENACAO_VALIDOS["clientes"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campo inválido. Use um de: {CAMPOS_ORDENACAO_VALIDOS['clientes']}"
        )
    direcao = 1 if ordem == "asc" else -1
    clientes = await Cliente.find().sort([(campo, direcao)]).limit(limite).to_list()
    return {"total": len(clientes), "ordenado_por": campo, "ordem": ordem, "clientes": clientes}


@router.get("/ordenar/veiculos", summary="Listar veículos com ordenação configurável")
async def veiculos_ordenados(
    campo: str = Query("modelo", description="Campo para ordenação: modelo, placa, tipo, status"),
    ordem: str = Query("asc", description="Direção: 'asc' para crescente, 'desc' para decrescente"),
    limite: int = Query(20, ge=1, le=100, description="Quantidade máxima de resultados (1-100)"),
):
    """
    Lista veículos com **ordenação configurável** por campo e direção.

    """
    if campo not in CAMPOS_ORDENACAO_VALIDOS["veiculos"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campo inválido. Use um de: {CAMPOS_ORDENACAO_VALIDOS['veiculos']}"
        )
    direcao = 1 if ordem == "asc" else -1
    veiculos = await Veiculo.find().sort([(campo, direcao)]).limit(limite).to_list()
    return {"total": len(veiculos), "ordenado_por": campo, "ordem": ordem, "veiculos": veiculos}


@router.get("/ordenar/alugueis", summary="Listar aluguéis com ordenação configurável")
async def alugueis_ordenados(
    campo: str = Query("data_inicio", description="Campo para ordenação: data_inicio, data_fim, status, pagamento.valor_total"),
    ordem: str = Query("desc", description="Direção: 'asc' para crescente, 'desc' para decrescente"),
    limite: int = Query(20, ge=1, le=100, description="Quantidade máxima de resultados (1-100)"),
):
    """
    Lista aluguéis com **ordenação configurável**, inclusive por campo de subdocumento (`pagamento.valor_total`).

    Demonstra **sort em campo embutido** usando notação de ponto do MongoDB.
    """
    if campo not in CAMPOS_ORDENACAO_VALIDOS["alugueis"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campo inválido. Use um de: {CAMPOS_ORDENACAO_VALIDOS['alugueis']}"
        )
    direcao = 1 if ordem == "asc" else -1
    alugueis = await Aluguel.find().sort([(campo, direcao)]).limit(limite).to_list()
    return {"total": len(alugueis), "ordenado_por": campo, "ordem": ordem, "alugueis": alugueis}


# ---------------------------------------------------------------------------
# 6. CONSULTAS COMPLEXAS COM MÚLTIPLAS COLEÇÕES ($lookup)
# ---------------------------------------------------------------------------

@router.get("/lookup/alugueis-completos", summary="Aluguéis com dados completos de cliente, veículo e ofertador")
async def alugueis_completos():
    """
    Retorna aluguéis enriquecidos com os dados completos de **cliente**, **veículo** e **ofertador**
    em uma única consulta usando `$lookup` encadeado entre três coleções.

    Demonstra **consulta complexa multi-coleção** com pipeline de agregação:
    `alugueis → $lookup → veiculos → $lookup → ofertador → $lookup → clientes`
    """
    collection = Aluguel.get_pymongo_collection()
    pipeline = [
        {"$lookup": {
            "from": "veiculos",
            "localField": "veiculo.$id",
            "foreignField": "_id",
            "as": "veiculo_dados",
        }},
        {"$unwind": {"path": "$veiculo_dados", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "ofertador",
            "localField": "veiculo_dados.ofertador.$id",
            "foreignField": "_id",
            "as": "ofertador_dados",
        }},
        {"$unwind": {"path": "$ofertador_dados", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "cliente",
            "localField": "cliente.$id",
            "foreignField": "_id",
            "as": "cliente_dados",
        }},
        {"$unwind": {"path": "$cliente_dados", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 1,
            "data_inicio": 1,
            "data_fim": 1,
            "status": 1,
            "pagamento": 1,
            "cliente": {"nome": "$cliente_dados.nome", "CPF": "$cliente_dados.CPF"},
            "veiculo": {"modelo": "$veiculo_dados.modelo", "placa": "$veiculo_dados.placa", "tipo": "$veiculo_dados.tipo"},
            "ofertador": {"nome": "$ofertador_dados.nome", "CNPJ": "$ofertador_dados.CNPJ"},
        }},
        {"$sort": {"data_inicio": -1}},
    ]
    cursor = collection.aggregate(pipeline)
    alugueis = []
    async for documento in cursor:
        if "_id" in documento:
            documento["_id"] = str(documento["_id"])
        alugueis.append(documento)
        
    return {
        "total": len(alugueis), 
        "alugueis": alugueis
    }


@router.get("/lookup/veiculos-com-comodidades", summary="Veículos com comodidades expandidas e ofertador")
async def veiculos_com_comodidades():
    """
    Retorna veículos com a lista de **comodidades expandida** (N:N resolvido via `$lookup`)
    e os dados do **ofertador** (1:N resolvido via `$lookup`).

    Demonstra **consulta multi-coleção** que resolve simultaneamente um relacionamento
    1:N (Ofertador → Veiculo) e um N:N (Veiculo ↔ Comodidade) em um único pipeline.
    """
    collection = Veiculo.get_pymongo_collection()
    pipeline = [
        {"$lookup": {
            "from": "comodidades",
            "localField": "comodidades.$id",
            "foreignField": "_id",
            "as": "comodidades_dados",
        }},
        {"$lookup": {
            "from": "ofertador",
            "localField": "ofertador.$id",
            "foreignField": "_id",
            "as": "ofertador_dados",
        }},
        {"$unwind": {"path": "$ofertador_dados", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 1,
            "placa": 1,
            "modelo": 1,
            "tipo": 1,
            "status": 1,
            "ofertador": {"nome": "$ofertador_dados.nome", "CNPJ": "$ofertador_dados.CNPJ"},
            "comodidades": {"$map": {
                "input": "$comodidades_dados",
                "as": "c",
                "in": {"nome": "$$c.nome", "descricao": "$$c.descricao"}
            }},
            "total_comodidades": {"$size": "$comodidades_dados"},
        }},
        {"$sort": {"total_comodidades": -1}},
    ]
    cursor = collection.aggregate(pipeline)
    veiculos = []
    async for documento in cursor:
        if "_id" in documento:
            documento["_id"] = str(documento["_id"])
        veiculos.append(documento)
        
    return {
        "total": len(veiculos), 
        "veiculos": veiculos
    }


@router.get("/lookup/ranking-ofertadores", summary="Ranking de ofertadores por número de aluguéis")
async def ranking_ofertadores():
    """
    Gera um ranking dos ofertadores com mais aluguéis realizados, cruzando três coleções:
    **alugueis → veiculos → ofertador**.

    Demonstra **pipeline de agregação multi-coleção** com `$lookup` encadeado,
    `$group` para agrupar por ofertador e `$sort` para ordenar o ranking.
    """
    collection = Aluguel.get_pymongo_collection()
    pipeline = [
        {"$lookup": {
            "from": "veiculos",
            "localField": "veiculo.$id",
            "foreignField": "_id",
            "as": "veiculo_dados",
        }},
        {"$unwind": {"path": "$veiculo_dados", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "ofertador",
            "localField": "veiculo_dados.ofertador.$id",
            "foreignField": "_id",
            "as": "ofertador_dados",
        }},
        {"$unwind": {"path": "$ofertador_dados", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id": "$ofertador_dados._id",
            "nome_ofertador": {"$first": "$ofertador_dados.nome"},
            "total_alugueis": {"$sum": 1},
            "receita_total": {"$sum": "$pagamento.valor_total"},
        }},
        {"$sort": {"total_alugueis": -1}},
        {"$project": {
            "_id": 0,
            "ofertador": "$nome_ofertador",
            "total_alugueis": 1,
            "receita_total": 1,
        }},
    ]
    cursor = collection.aggregate(pipeline)
    resultado = []
    async for documento in cursor:
        resultado.append(documento)
    return {"resultado": resultado}