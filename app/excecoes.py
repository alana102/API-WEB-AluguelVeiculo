from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

def configurar_excecoes_globais(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validacao_exception_handler(request: Request, exc: RequestValidationError):
        erros = []
        for erro in exc.errors():
            campo = " -> ".join([str(loc) for loc in erro["loc"]])
            mensagem = erro["msg"]
            erros.append(f"Erro no campo '{campo}': {mensagem}")
            
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "mensagem": "Erro de validação nos dados enviados.",
                "detalhes": erros
            }
        )
    @app.exception_handler(Exception)
    async def erro_generico_handler(request: Request, exc: Exception):
        print(f"Erro Crítico Interceptado: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensagem": "Ocorreu um erro interno no servidor. Nossa equipe já foi notificada."}
        )