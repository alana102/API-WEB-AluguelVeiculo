from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi_pagination import add_pagination

from app.config.settings import settings
from app.config.minio_client import init_minio
from app.modelos.documento import DocumentoModel

from app.modelos.veiculo import Veiculo
from app.modelos.ofertador import Ofertador
from app.modelos.cliente import Cliente
from app.modelos.aluguel import Aluguel

from app.rotas import veiculo_rotas, cliente_rotas, ofertador_rotas, aluguel_rotas, documento_rotas
from app.excecoes import configurar_excecoes_globais

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    client.__dict__["append_metadata"] = lambda *args, **kwargs: None
    db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0]
    db = client[db_name]

    await init_beanie(
        database=db, 
        document_models=[Veiculo, Ofertador, Cliente, Aluguel, DocumentoModel]
    )

    await init_minio()

    yield

app = FastAPI(title="API WEB - Aluguel de Veículos", lifespan=lifespan)

configurar_excecoes_globais(app)
app.include_router(cliente_rotas.router)
app.include_router(ofertador_rotas.router)
app.include_router(veiculo_rotas.router)
app.include_router(aluguel_rotas.router)
app.include_router(documento_rotas.rotas)

add_pagination(app)