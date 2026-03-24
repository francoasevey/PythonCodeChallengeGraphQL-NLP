from fastapi import FastAPI
from auth_service.schemas import TokenRequest, TokenResponse
from auth_service.jwt_handler import create_access_token
from auth_service.config import settings

app = FastAPI(title="Auth Service", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth_service"}


@app.post("/token", response_model=TokenResponse)
def token(body: TokenRequest):
    # TODO: implementar en tarea 2
    pass
