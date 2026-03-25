from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_service.routers.graphql import graphql_router
from data_service.routers.nlp import router as nlp_router
from data_service.services.csv_service import load_dataframe
from data_service.middleware.auth import verify_token
from fastapi import Depends


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


@app.get("/stats", tags=["Stats"], summary="Estadísticas del dataset CSV")
def stats(_: dict = Depends(verify_token)):
    df = load_dataframe()
    top_category = (
        df["desc_categoria_prod_principal"]
        .replace("", None)
        .dropna()
        .value_counts()
        .idxmax()
    )
    top_brand = (
        df[~df["desc_ga_marca_producto"].isin(["", "No Aplica"])]
        ["desc_ga_marca_producto"]
        .value_counts()
        .idxmax()
    )
    return {
        "total_records": len(df),
        "unique_brands": int(
            df[~df["desc_ga_marca_producto"].isin(["", "No Aplica"])]
            ["desc_ga_marca_producto"].nunique()
        ),
        "unique_categories": int(
            df["desc_categoria_prod_principal"].replace("", None).dropna().nunique()
        ),
        "unique_clients": int(df["id_cli_cliente"].nunique()),
        "date_range": {
            "from": df["id_tie_fecha_valor"].min(),
            "to": df["id_tie_fecha_valor"].max(),
        },
        "top_category": top_category,
        "top_brand": top_brand,
    }
