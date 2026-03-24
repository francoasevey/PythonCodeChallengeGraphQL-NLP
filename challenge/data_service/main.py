from fastapi import FastAPI

app = FastAPI(title="Data Service", version="1.0.0")

# TODO tarea 8: incluir router graphql
# TODO tarea 9: incluir router nlp


@app.get("/health")
def health():
    return {"status": "ok", "service": "data_service"}
