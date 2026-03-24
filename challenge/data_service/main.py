from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_service.routers.graphql import graphql_router
from data_service.routers.nlp import router as nlp_router
from data_service.services.csv_service import load_dataframe


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dataframe()  # precarga el CSV en memoria al arrancar
    yield


app = FastAPI(
    title="Data Service",
    version="1.0.0",
    description="GraphQL y NLP sobre dataset de interacciones de e-commerce.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(graphql_router, prefix="/graphql")
app.include_router(nlp_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "data_service"}
