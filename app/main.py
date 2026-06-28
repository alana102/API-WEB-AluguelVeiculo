from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config.settings import settings
from app.config.minio_client import init_minio
from app.modelos.documento import DocumentoModel
from app.rotas.documento_rotas import rotas as documento_rotas

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    client.__dict__["append_metadata"] = lambda *args, **kwargs: None
    db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0]
    db = client[db_name]

    await init_beanie(
        database=db, 
        document_models=[DocumentoModel]
    )

    await init_minio()

    yield

app = FastAPI(title="API WEB - Aluguel de Veículos", lifespan=lifespan)

app.include_router(documento_rotas)