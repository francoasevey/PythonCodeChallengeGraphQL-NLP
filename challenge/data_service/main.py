from fastapi import FastAPI

from data_service.routers.graphql import graphql_router
from data_service.routers.nlp import router as nlp_router

app = FastAPI(title="Data Service", version="1.0.0")

app.include_router(graphql_router, prefix="/graphql")
app.include_router(nlp_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "data_service"}
