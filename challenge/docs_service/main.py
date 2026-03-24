from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse

from docs_service.aggregator import fetch_and_merge_specs

_spec_cache: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _spec_cache
    _spec_cache = await fetch_and_merge_specs()
    yield


app = FastAPI(
    title="Docs Service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


@app.get("/openapi.json", include_in_schema=False)
async def openapi_spec() -> JSONResponse:
    return JSONResponse(_spec_cache)


@app.get("/docs", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="CFOTech Challenge API — Unified Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok", "service": "docs_service"}
