from fastapi import FastAPI, HTTPException, status

from auth_service.config import settings
from auth_service.jwt_handler import create_access_token
from auth_service.schemas import TokenRequest, TokenResponse

app = FastAPI(title="Auth Service", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth_service"}


@app.post("/token", response_model=TokenResponse)
def token(body: TokenRequest):
    if body.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="grant_type must be client_credentials",
        )
    if body.client_id != settings.client_id or body.client_secret != settings.client_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )
    access_token = create_access_token({"sub": body.client_id})
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )
