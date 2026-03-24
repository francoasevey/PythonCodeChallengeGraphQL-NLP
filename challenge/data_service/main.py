from fastapi import FastAPI

from data_service.routers.graphql import graphql_router

app = FastAPI(title="Data Service", version="1.0.0")

app.include_router(graphql_router, prefix="/graphql")

# TODO tarea 9: incluir router nlp


@app.get("/health")
def health():
    return {"status": "ok", "service": "data_service"}
