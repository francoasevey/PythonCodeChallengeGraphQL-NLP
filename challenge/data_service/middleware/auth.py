from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from data_service.config import settings

http_bearer = HTTPBearer(auto_error=True)


def verify_token_raw(token: str) -> dict:
    """Valida el JWT y retorna el payload. Lanza HTTPException si es inválido."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    """Dependency para endpoints HTTP normales (NLP)."""
    return verify_token_raw(credentials.credentials)
