from fastapi import FastAPI

app = FastAPI(
    title="Aluguel de Veículos",
    description="API Web de aluguel de veículos com FastAPI, MongoDB e MinIO"
)

@app.get("/")
async def root():
    return {"message": "Ambiente configurado! Banco de dados e MinIO em breve."}