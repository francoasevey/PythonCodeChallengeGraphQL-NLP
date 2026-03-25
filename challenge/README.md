# Python Code Challenge — GraphQL & NLP API

**Candidato:** Franco
**Rol:** Semi-Senior FullStack Python Developer — CFOTech

API dockerizada con tres microservicios: autenticación OAuth2/JWT, datos vía GraphQL y NLP con Claude API, y documentación Swagger unificada.

---

## Servicios

| Servicio | Puerto | Descripción |
|---|---|---|
| `auth_service` | 8002 | OAuth2 client credentials flow — emite JWT |
| `data_service` | 8001 | GraphQL + NLP sobre dataset CSV |
| `docs_service` | 8000 | Swagger UI unificado (agrega specs de los otros servicios) |

---

## Setup

### Prerequisitos

- Docker Desktop instalado y corriendo
- Cuenta en [Anthropic Console](https://console.anthropic.com) para obtener `ANTHROPIC_API_KEY`

### 1. Clonar el repositorio

```bash
git clone https://github.com/francoasevey/PythonCodeChallengeGraphQL-NLP.git
cd PythonCodeChallengeGraphQL-NLP/challenge
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con los valores reales:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave para firmar JWT (mínimo 32 caracteres) |
| `CLIENT_ID` | ID del cliente OAuth2 |
| `CLIENT_SECRET` | Secret del cliente OAuth2 |
| `ANTHROPIC_API_KEY` | API key de Claude (Anthropic) |

### 3. Levantar los servicios

```bash
docker-compose up --build
```

El orden de startup es automático:
`auth_service` → `data_service` → `docs_service`

Cada servicio espera que el anterior esté healthy antes de arrancar.

---

## Uso

### Obtener token JWT

Las credenciales por defecto están definidas en `.env.example`:

| Variable | Valor por defecto |
|---|---|
| `CLIENT_ID` | `cfotech-client` |
| `CLIENT_SECRET` | `cfotech-secret` |

**curl:**
```bash
curl -X POST http://localhost:8002/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "cfotech-client",
    "client_secret": "cfotech-secret",
    "grant_type": "client_credentials"
  }'
```

**Desde Swagger UI (`http://localhost:8000/docs`):**
1. Abrí `POST /token` → **Try it out**
2. El body ya viene pre-completado — click **Execute**
3. Copiá el `access_token` de la respuesta
4. Click en **Authorize 🔒** (arriba a la derecha) → pegá el token → **Authorize** → Close
5. Todos los endpoints protegidos (🔒) incluirán el header automáticamente

Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Guardar el token en terminal para los siguientes requests:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### GraphQL

#### Opción A — Playground interactivo (recomendado)

1. Abrí `http://localhost:8001/graphql` en el browser
2. Click en **Headers** (panel inferior)
3. Pegá el token:
```json
{ "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```
4. Escribí la query en el panel izquierdo y click **▶ Run**

#### Opción B — curl

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8001/graphql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ topBrands(limit: 5) { brand count } }"}'
```

---

#### Schema GraphQL

**Tipo `ProductInteraction`** — una fila del dataset CSV:

| Campo | Tipo | Descripción |
|---|---|---|
| `date` | String | Fecha del evento formato `YYYYMMDD` |
| `clientId` | String | ID hasheado del cliente |
| `productName` | String | Nombre completo del producto |
| `brand` | String | Marca del producto |
| `sku` | String | Código SKU del producto |
| `category` | String | Categoría principal (ej: `PINTURAS Y ACCESORIOS/...`) |
| `cartAdditions` | String | Veces agregado al carrito |
| `cartRemovals` | String | Veces retirado del carrito |
| `quantitySold` | String | Unidades vendidas |
| `revenue` | String | Ingreso generado |
| `productDetailViews` | String | Vistas al detalle del producto |
| `pageViews` | String | Visualizaciones de página |

**Tipo `BrandCount`** — resultado agregado:

| Campo | Tipo | Descripción |
|---|---|---|
| `brand` | String | Nombre de la marca |
| `count` | Int | Frecuencia de aparición en el dataset |

---

#### Queries disponibles

**1. Listado paginado — `productInteractions`**
```graphql
{
  productInteractions(limit: 3, offset: 0) {
    date
    productName
    brand
    category
    cartAdditions
    revenue
  }
}
```

Respuesta real:
```json
{
  "data": {
    "productInteractions": [
      {
        "date": "20240129",
        "productName": "TERMO CLÁSICO STANLEY 950 ML CON MANIJA Y TAPON CEBADOR VERDE",
        "brand": "STANLEY",
        "category": "JARDÍN Y AIRE LIBRE/CAMPING Y PLAYA/TERMOS",
        "cartAdditions": "0",
        "revenue": "0"
      }
    ]
  }
}
```

**2. Filtrar por categoría — `productsByCategory`**

Búsqueda parcial, case-insensitive. Categorías disponibles: `PINTURAS`, `ESMALTES`, `JARDIN`, `HERRAMIENTAS`, etc.

```graphql
{
  productsByCategory(category: "PINTURAS", limit: 5) {
    productName
    brand
    sku
    cartAdditions
  }
}
```

Respuesta real:
```json
{
  "data": {
    "productsByCategory": [
      {
        "productName": "ENDUIDO INTERIOR CASABLANCA 1 LT",
        "brand": "CASABLANCA",
        "sku": "SUCEI01",
        "cartAdditions": "1"
      },
      {
        "productName": "LATEX INTERIOR ALBALATEX ULTRALAVABLE MATE BLANCO 20 LTS ALBA",
        "brand": "ALBA",
        "sku": "ATUL20",
        "cartAdditions": "2"
      }
    ]
  }
}
```

**3. Top marcas — `topBrands`**

```graphql
{
  topBrands(limit: 5) {
    brand
    count
  }
}
```

Respuesta real:
```json
{
  "data": {
    "topBrands": [
      { "brand": "ALBA", "count": 1393 },
      { "brand": "SINTEPLAST", "count": 1164 },
      { "brand": "TERSUAVE", "count": 961 },
      { "brand": "SHERWIN WILLIAMS", "count": 723 },
      { "brand": "LÜSQTOFF", "count": 687 }
    ]
  }
}
```

**4. Filtrar por rango de fechas — `interactionsByDateRange`**

Formato de fechas: `YYYYMMDD`. El dataset cubre del `20240129` al `20240131`.

```graphql
{
  interactionsByDateRange(dateFrom: "20240129", dateTo: "20240130", limit: 5) {
    date
    productName
    brand
  }
}
```

---

#### Introspección del schema

Para explorar el schema completo desde el playground:

```graphql
{
  __schema {
    types {
      name
      fields {
        name
        description
        type { name }
      }
    }
  }
}
```

---

### NLP

Consultas en lenguaje natural sobre el dataset. Claude API responde en español.

> **Rate limit:** 10 requests/minuto por IP. Superar el límite retorna `429 Too Many Requests`.

```bash
curl -X POST http://localhost:8001/nlp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuáles son las marcas más frecuentes en el dataset?"}'
```

```bash
curl -X POST http://localhost:8001/nlp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué categorías de productos tienen más interacciones?"}'
```

```bash
curl -X POST http://localhost:8001/nlp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuál es el rango de fechas del dataset?"}'
```

Respuesta:
```json
{
  "question": "¿Cuáles son las marcas más frecuentes en el dataset?",
  "answer": "Las marcas más frecuentes en el dataset son ALBA (1393 apariciones), SINTEPLAST (1164), TERSUAVE (961), SHERWIN WILLIAMS (723) y LOCTITE (687). El dataset está dominado por productos de pinturas y revestimientos."
}
```

---

### Estadísticas del dataset

Resumen estadístico del CSV — total de registros, marcas, categorías, clientes únicos y rango de fechas.

```bash
curl http://localhost:8001/stats \
  -H "Authorization: Bearer $TOKEN"
```

Respuesta:
```json
{
  "total_records": 5000,
  "unique_brands": 245,
  "unique_categories": 12,
  "unique_clients": 3421,
  "date_range": { "from": "20240129", "to": "20240131" },
  "top_category": "PINTURAS Y ACCESORIOS/PINTURAS INTERIOR",
  "top_brand": "ALBA"
}
```

---

### Swagger UI unificado

Documentación completa de todos los endpoints en un solo lugar:

```
http://localhost:8000/docs
```

Para probar desde el Swagger UI:
1. Ejecutar `POST /token` con las credenciales → copiar el `access_token`
2. Click en **Authorize 🔒** (arriba a la derecha) → pegar el token → Close
3. Todos los endpoints protegidos incluirán el header automáticamente

---

### Landing page

Página de bienvenida con links a todos los servicios:

```
http://localhost:8000/
```

---

### Health checks

```bash
curl http://localhost:8002/health  # auth_service
curl http://localhost:8001/health  # data_service
curl http://localhost:8000/health  # docs_service
```

---

## Arquitectura

```mermaid
graph TD
    Client(["Cliente / Evaluador"])

    subgraph Docker["Docker Compose"]
        Auth["auth_service<br/>:8002<br/>OAuth2 + JWT"]
        Data["data_service<br/>:8001<br/>GraphQL + NLP"]
        Docs["docs_service<br/>:8000<br/>Swagger UI"]
    end

    CSV[("dataset.csv")]
    Claude(["Claude API<br/>(Anthropic)"])

    Client -->|"POST /token<br/>client_id + secret"| Auth
    Auth -->|"JWT Bearer token"| Client
    Client -->|"POST /graphql<br/>Bearer token"| Data
    Client -->|"POST /nlp<br/>Bearer token"| Data
    Client -->|"GET /docs"| Docs
    Docs -->|"agrega specs en startup"| Auth
    Docs -->|"agrega specs en startup"| Data
    Data -->|"lee CSV"| CSV
    Data -->|"NLP query"| Claude
```

**Estructura de carpetas:**

```
challenge/
├── auth_service/       # OAuth2 + JWT — Puerto 8002
├── data_service/       # GraphQL + NLP — Puerto 8001
│   ├── routers/        # graphql.py, nlp.py
│   ├── services/       # csv_service.py, nlp_service.py
│   ├── schema/         # Strawberry types y resolvers
│   ├── models/         # Pydantic DTOs
│   └── middleware/     # JWT verify_token
├── docs_service/       # Swagger unificado — Puerto 8000
├── data/               # dataset.csv
├── docker-compose.yml
└── .env.example
```

**Decisiones técnicas clave:**
- JWT validado localmente en `data_service` con secret compartido — sin round-trip HTTP a `auth_service` por request
- NLP usa contexto estructurado con pandas (no raw CSV) como system prompt de Claude
- GraphQL protegido via `context_getter` de Strawberry — no middleware HTTP genérico
- `docs_service` agrega specs dinámicamente en startup desde `/openapi.json` de cada servicio
- CSV precargado en memoria con `lifespan` — sin latencia en el primer request

---

## Stack

| Componente | Tecnología |
|---|---|
| Framework | FastAPI |
| GraphQL | Strawberry |
| NLP | Claude API (Anthropic) — `claude-opus-4-5` |
| JWT / OAuth2 | python-jose |
| Validación | Pydantic v2 |
| CSV | pandas |
| Containerización | Docker + docker-compose |

---

## IA utilizada

**Claude (Anthropic)** — utilizado como asistente durante la planificación y desarrollo. Conversaciones adjuntas en PDF según los lineamientos del challenge.

Claude también es el modelo detrás del endpoint `/nlp` en producción (Claude API).
