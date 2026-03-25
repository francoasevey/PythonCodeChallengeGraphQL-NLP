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
    "Auth Service": {
        "internal_url": settings.auth_service_url_docs,
        "external_url": "http://localhost:8002",
    },
    "Data Service": {
        "internal_url": settings.data_service_url,
        "external_url": "http://localhost:8001",
    },
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
    "components": {
        "schemas": {},
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT obtenido en POST /token. Formato: Bearer <token>",
            }
        },
    },
    "security": [],
}


async def fetch_spec(name: str, internal_url: str) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{internal_url}/openapi.json")
        response.raise_for_status()
        return response.json()


def _merge_into(merged: dict, spec: dict, external_url: str) -> None:
    """Merge paths injecting path-level server override so Swagger UI Try it out works."""
    server_override = [{"url": external_url}]
    for path, path_item in spec.get("paths", {}).items():
        path_item_copy = dict(path_item)
        path_item_copy["servers"] = server_override
        merged["paths"][path] = path_item_copy
    schemas = spec.get("components", {}).get("schemas", {})
    merged["components"]["schemas"].update(schemas)


async def fetch_and_merge_specs() -> dict:
    import copy
    merged = copy.deepcopy(MERGED_SPEC_BASE)
    for name, config in SERVICES.items():
        try:
            spec = await fetch_spec(name, config["internal_url"])
            _merge_into(merged, spec, config["external_url"])
        except Exception as exc:
            merged["paths"][f"/_unavailable/{name.lower().replace(' ', '_')}"] = {
                "get": {
                    "summary": f"{name} unavailable",
                    "description": f"No se pudo obtener la spec: {exc}",
                    "responses": {"503": {"description": "Service Unavailable"}},
                }
            }
    return merged
