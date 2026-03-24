# Challenge — Reglas y Arquitectura

## El Challenge

Desarrollar una API con los siguientes servicios y endpoints:

**Data Service**
- Conectarse a un archivo CSV (se descarga del enunciado)
- Endpoint GraphQL con schema completo y documentado
- Endpoint NLP: consulta en lenguaje natural sobre los datos del CSV, responde en lenguaje natural

**Docs Service**
- Swagger/OpenAPI 3.0 documentando todos los endpoints, con ejemplos reales del dataset

**Auth Service (opcional pero se implementa)**
- OAuth2 client credentials flow
- Retorna JWT
- El JWT es requerido como Bearer token en Authorization header para los endpoints del Data Service

**Requisitos generales**
- Todo en Docker
- Repositorio público en GitHub con commits progresivos reales (no un commit final)
- README explicando cómo compilar y levantar
- Se acepta uso de IA pero hay que entregar los chats en PDF

---

## Decisiones de Arquitectura

**Nivel 1 — Distribución del sistema:** Microservicios — 3 contenedores Docker separados (`auth_service`, `data_service`, `docs_service`)

**Nivel 2 — Organización interna:** N-Layer simplificada — `router → service → data`. Sin Clean Architecture pura ni Hexagonal (over-engineering para este scope)

**Nivel 3 — Patrones:** SOLID aplicado naturalmente, Repository pattern para `csv_service`, Dependency Injection con `FastAPI Depends()`, DTOs con Pydantic v2

---

## Stack Tecnológico

- **FastAPI** para los 3 servicios
- **Strawberry** para GraphQL (tipado con Python type hints, integración nativa con FastAPI)
- **Claude API (Anthropic)** para el endpoint NLP
- **python-jose** para JWT y OAuth2
- **Pydantic v2** para validación y DTOs
- **pandas** para lectura y agregación del CSV
- **Docker + docker-compose**
- **python-dotenv + .env** para configuración

---

## Estructura de Carpetas

```
challenge/
├── auth_service/
│   ├── main.py              (~40 líneas)
│   ├── jwt_handler.py       (~60 líneas)
│   ├── schemas.py           (~20 líneas)
│   └── config.py            (~20 líneas)
├── data_service/
│   ├── main.py              (~30 líneas)
│   ├── routers/
│   │   ├── graphql.py       (~50 líneas)
│   │   └── nlp.py           (~40 líneas)
│   ├── services/
│   │   ├── csv_service.py   (~80 líneas — carga, expone datos crudos y contexto agregado)
│   │   └── nlp_service.py   (~60 líneas — Claude API client con contexto inteligente)
│   ├── schema/
│   │   └── types.py         (~60 líneas — Strawberry types con nombres legibles)
│   ├── models/
│   │   └── schemas.py       (~40 líneas — Pydantic DTOs + ErrorResponse estándar)
│   ├── middleware/
│   │   └── auth.py          (~30 líneas — valida Bearer token vía Depends())
│   └── config.py            (~20 líneas)
├── docs_service/
│   ├── main.py              (~50 líneas — agrega specs de los otros servicios)
│   └── aggregator.py        (~80 líneas — fetch /openapi.json de cada servicio y merge)
├── data/
│   └── dataset.csv
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Decisiones Técnicas Clave

### docs_service — Opción A: Agregación dinámica

`docs_service` hace `GET http://data_service:8001/openapi.json` y
`GET http://auth_service:8002/openapi.json` en startup, los agrega y sirve
un Swagger UI unificado. Esto refleja arquitectura de microservicios real.

```python
# docs_service/aggregator.py
import httpx

SERVICES = {
    "data_service": "http://data_service:8001/openapi.json",
    "auth_service": "http://auth_service:8002/openapi.json",
}

async def fetch_and_merge_specs() -> dict:
    merged = {
        "openapi": "3.0.0",
        "info": {"title": "Challenge API — Unified Docs", "version": "1.0.0"},
        "paths": {},
        "components": {"schemas": {}},
    }
    async with httpx.AsyncClient() as client:
        for name, url in SERVICES.items():
            try:
                resp = await client.get(url, timeout=5.0)
                spec = resp.json()
                merged["paths"].update(spec.get("paths", {}))
                merged["components"]["schemas"].update(
                    spec.get("components", {}).get("schemas", {})
                )
            except Exception:
                pass  # servicio no disponible, continúa
    return merged
```

---

### NLP — Contexto inteligente con pandas (no raw CSV)

El CSV tiene 23 columnas y muchas filas. No se manda completo a Claude.
Se construye un contexto agregado en `csv_service.py`:

```python
# data_service/services/csv_service.py
def build_nlp_context(df: pd.DataFrame) -> str:
    return f"""
Dataset: e-commerce product interactions ({len(df)} rows, {len(df.columns)} columns)

Columns: {', '.join(df.columns.tolist())}

Sample data (5 rows):
{df.head(5).to_markdown()}

Key stats:
- Date range: {df['id_tie_fecha_valor'].min()} to {df['id_tie_fecha_valor'].max()}
- Unique clients: {df['id_cli_cliente'].nunique()}
- Device types: {df['id_ga_tipo_dispositivo'].unique().tolist()}
- Top categories: {df['glb_d_categoria'].value_counts().head(5).to_dict()}
- Top brands: {df['glb_d_marca'].value_counts().head(5).to_dict()}
""".strip()
```

Este string va como system prompt a Claude. La pregunta del usuario va como user message.

---

### GraphQL — JWT via context_getter (no middleware HTTP)

Strawberry maneja su propio request lifecycle. El middleware HTTP estándar
de FastAPI no intercepta bien el endpoint `/graphql`. La forma correcta:

```python
# data_service/routers/graphql.py
from strawberry.fastapi import GraphQLRouter
from data_service.middleware.auth import verify_token

async def get_context(request: Request, user: dict = Depends(verify_token)):
    return {"request": request, "user": user}

graphql_router = GraphQLRouter(schema, context_getter=get_context)
```

Esto permite que el playground de GraphQL funcione correctamente y que
la validación del token sea parte del ciclo de vida de Strawberry.

---

### GraphQL Schema — Columnas mapeadas a nombres legibles

Las columnas del CSV tienen nombres internos crípticos. El schema de
Strawberry las mapea a nombres legibles con `strawberry.field`:

```python
# data_service/schema/types.py
@strawberry.type
class ProductInteraction:
    date: str = strawberry.field(description="Fecha del evento")
    client_id: str = strawberry.field(description="ID del cliente")
    device_type: str = strawberry.field(description="Tipo de dispositivo (mobile, desktop, tablet)")
    traffic_source: str = strawberry.field(description="Fuente de tráfico (GA source/medium)")
    category: str = strawberry.field(description="Categoría del producto")
    brand: str = strawberry.field(description="Marca del producto")
    sku: str = strawberry.field(description="SKU del producto")
    product_name: str = strawberry.field(description="Nombre del producto")
```

Queries útiles expuestos dado el dataset:
- `productInteractions(limit: Int, offset: Int)` — paginación básica
- `productsByCategory(category: String!)` — filtro por categoría
- `interactionsByDevice(deviceType: String!)` — filtro por dispositivo
- `topBrands(limit: Int = 10)` — agregación de marcas más activas
- `interactionsByDateRange(from: String!, to: String!)` — rango de fechas

---

### docker-compose — depends_on + healthcheck

Evita que `data_service` arranque antes que `auth_service`:

```yaml
# docker-compose.yml (fragmento)
auth_service:
  build: ./auth_service
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
    interval: 10s
    timeout: 5s
    retries: 3

data_service:
  build: ./data_service
  depends_on:
    auth_service:
      condition: service_healthy

docs_service:
  build: ./docs_service
  depends_on:
    data_service:
      condition: service_healthy
    auth_service:
      condition: service_healthy
```

---

### Error responses — Formato estándar con Pydantic

```python
# data_service/models/schemas.py
class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int

# Uso en routers
@router.get("/nlp", responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
```

---

## Reglas de Modularización

- Máximo ~150 líneas por archivo
- Máximo ~30 líneas por función
- Si un archivo tiene imports de más de 2 módulos distintos → señal de mezcla de responsabilidades
- `csv_service.py` expone datos crudos Y el contexto agregado para NLP — transformaciones específicas van en cada consumer
- `__init__.py` con exports explícitos en cada carpeta para imports limpios

---

## Qué NO Implementar

- Arquitectura Hexagonal (over-engineering)
- Clean Architecture pura con use cases (burocracia sin valor)
- Base de datos (piden CSV)
- Redis / Celery / message queues (no hay justificación)
- OOP forzada con clases en FastAPI (es funcional, respetar el paradigma)
- Tests exhaustivos (no los piden)

---

## Qué SÍ Implementar Para Destacar

- NLP con Claude API real (no filtro por keywords) — diferenciador principal
- Contexto inteligente con pandas para Claude (no raw CSV)
- Swagger unificado vía agregación dinámica de specs (Opción A)
- JWT via `context_getter` en Strawberry — no middleware HTTP genérico
- GraphQL con columnas mapeadas a nombres legibles + queries de filtrado/agregación
- `/health` endpoint en cada servicio
- `depends_on` + `healthcheck` en docker-compose
- Formato de error estándar con Pydantic en todos los endpoints
- `.env.example` con todas las variables documentadas
- Commits atómicos con prefijos `feat/fix/chore` por feature
- README nivel producción: setup, variables, ejemplos curl, decisiones de arquitectura

---

## Orden de Implementación

```
Sábado AM:  auth_service completo + JWT flow testeado con curl
Sábado PM:  csv_service (carga CSV + build_nlp_context) + GraphQL schema + queries básicas
Domingo AM: NLP service con contexto inteligente + Claude API integration
Domingo PM: docs_service (agregación dinámica) + docker-compose completo + README + .env.example
Domingo N:  commits atómicos limpios, push, revisión final
```

---

## Puertos de Cada Servicio

| Servicio | Puerto |
|---|---|
| auth_service | 8002 |
| data_service | 8001 |
| docs_service | 8000 |

---

## Variables de Entorno (.env.example)

```env
# Auth Service
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

# Data Service
AUTH_SERVICE_URL=http://auth_service:8002
CSV_PATH=/data/dataset.csv

# NLP (Claude API)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Docs Service
DATA_SERVICE_URL=http://data_service:8001
AUTH_SERVICE_URL=http://auth_service:8002
```
