# Python Code Challenge — GraphQL & NLP API

> Semi-Senior FullStack Python Developer — CFOTech

## Servicios

| Servicio | Puerto | Descripción |
|---|---|---|
| `auth_service` | 8002 | OAuth2 client credentials + JWT |
| `data_service` | 8001 | GraphQL + NLP sobre dataset CSV |
| `docs_service` | 8000 | Swagger UI unificado |

---

## Setup

### 1. Clonar el repositorio

```bash
git clone https://github.com/francoasevey/PythonCodeChallengeGraphQL-NLP.git
cd challenge
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con los valores reales
```

### 3. Levantar los servicios

```bash
docker-compose up --build
```

---

*README completo — en progreso*
