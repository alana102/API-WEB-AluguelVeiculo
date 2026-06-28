from miniopy_async import Minio
from app.config.settings import settings

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False  
)

async def init_minio():
    """Garante que o bucket configurado exista no MinIO ao iniciar a API."""
    try:
        exists = await minio_client.bucket_exists(settings.MINIO_BUCKET_NAME)
        if not exists:
            await minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            print(f"🪣 Bucket '{settings.MINIO_BUCKET_NAME}' criado com sucesso!")
        else:
            print(f"🪣 Bucket '{settings.MINIO_BUCKET_NAME}' já existe.")
    except Exception as e:
        print(f"Erro ao conectar ou criar bucket no MinIO: {e}")