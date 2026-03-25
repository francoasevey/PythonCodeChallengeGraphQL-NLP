from typing import Optional

import strawberry
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from strawberry.fastapi import GraphQLRouter

from data_service.middleware.auth import verify_token_raw
from data_service.schema.types import Query

schema = strawberry.Schema(query=Query)

_bearer_optional = HTTPBearer(auto_error=False)


async def get_context(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_optional),
) -> dict:
    """GET → playground sin auth. POST → requiere Bearer token."""
    if request.method == "GET":
        return {"user": None}
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return {"user": verify_token_raw(credentials.credentials)}


graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True,
)
