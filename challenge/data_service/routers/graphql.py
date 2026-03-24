from typing import AsyncGenerator

import strawberry
from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from data_service.middleware.auth import verify_token
from data_service.schema.types import Query

schema = strawberry.Schema(query=Query)


async def get_context(user: dict = Depends(verify_token)) -> AsyncGenerator:
    return {"user": user}


graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True,
)
