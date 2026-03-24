import httpx
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_service_url: str = "http://data_service:8001"
    auth_service_url_docs: str = "http://auth_service:8002"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

SERVICES = {
    "Auth Service": settings.auth_service_url_docs,
    "Data Service": settings.data_service_url,
}

MERGED_SPEC_BASE: dict = {
    "openapi": "3.0.0",
    "info": {
        "title": "CFOTech Challenge API — Unified Docs",
        "version": "1.0.0",
        "description": (
            "Documentación unificada de los servicios Auth y Data. "
            "Autenticarse primero en POST /token para obtener el Bearer JWT "
            "requerido en los endpoints de Data Service."
        ),
    },
    "paths": {},
    "components": {"schemas": {}},
}


async def fetch_spec(name: str, base_url: str) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{base_url}/openapi.json")
        response.raise_for_status()
        return response.json()


def _merge_into(merged: dict, spec: dict) -> None:
    merged["paths"].update(spec.get("paths", {}))
    schemas = spec.get("components", {}).get("schemas", {})
    merged["components"]["schemas"].update(schemas)


async def fetch_and_merge_specs() -> dict:
    import copy
    merged = copy.deepcopy(MERGED_SPEC_BASE)
    for name, url in SERVICES.items():
        try:
            spec = await fetch_spec(name, url)
            _merge_into(merged, spec)
        except Exception as exc:
            merged["paths"][f"/_unavailable/{name.lower().replace(' ', '_')}"] = {
                "get": {
                    "summary": f"{name} unavailable",
                    "description": f"No se pudo obtener la spec: {exc}",
                    "responses": {"503": {"description": "Service Unavailable"}},
                }
            }
    return merged
