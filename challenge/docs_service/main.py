from fastapi import FastAPI

app = FastAPI(title="Docs Service", version="1.0.0")

# TODO tarea 12: montar Swagger UI unificado con spec de aggregator


@app.get("/health")
def health():
    return {"status": "ok", "service": "docs_service"}
