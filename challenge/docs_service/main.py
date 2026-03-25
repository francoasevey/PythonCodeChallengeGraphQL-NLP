from contextlib import asynccontextmanager

from fastapi import FastAPI
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
    html = """<!DOCTYPE html>
<html>
  <head>
    <title>CFOTech Challenge API — Unified Docs</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
      SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        layout: "StandaloneLayout",
        requestInterceptor: (req) => {
          try {
            const u = new URL(req.url);
            if (u.pathname === "/token") {
              req.url = "http://localhost:8002" + u.pathname + u.search;
            } else if (["/graphql", "/nlp"].some(p => u.pathname.startsWith(p))) {
              req.url = "http://localhost:8001" + u.pathname + u.search;
            }
          } catch(_) {}
          return req;
        }
      });
    </script>
  </body>
</html>"""
    return HTMLResponse(html)


@app.get("/", include_in_schema=False)
async def landing() -> HTMLResponse:
    html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CFOTech Challenge API</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
    .container { max-width: 820px; width: 100%; padding: 2rem; }
    h1 { font-size: 2rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.25rem; }
    .subtitle { color: #94a3b8; margin-bottom: 2.5rem; font-size: 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; }
    .card h3 { font-size: 1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.5rem; }
    .card .port { font-size: 0.75rem; color: #64748b; font-family: monospace; margin-bottom: 0.75rem; }
    .card p { font-size: 0.875rem; color: #94a3b8; line-height: 1.5; margin-bottom: 1rem; }
    .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.7rem; font-weight: 600; }
    .badge-green { background: #14532d; color: #4ade80; }
    .links { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.75rem; }
    .link { color: #38bdf8; text-decoration: none; font-size: 0.85rem; }
    .link:hover { color: #7dd3fc; }
    .flow { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; }
    .flow h2 { font-size: 1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; }
    .steps { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
    .step { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.8rem; color: #94a3b8; }
    .arrow { color: #475569; font-size: 1rem; }
    .footer { text-align: center; color: #475569; font-size: 0.8rem; }
    .footer a { color: #38bdf8; text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <h1>CFOTech Challenge API</h1>
    <p class="subtitle">Franco — Semi-Senior FullStack Python Developer &nbsp;·&nbsp; 3 microservicios &nbsp;·&nbsp; GraphQL + NLP + OAuth2</p>

    <div class="grid">
      <div class="card">
        <h3>Auth Service</h3>
        <div class="port">localhost:8002</div>
        <p>OAuth2 client credentials flow. Emite JWT Bearer tokens para acceder al Data Service.</p>
        <span class="badge badge-green">activo</span>
        <div class="links">
          <a class="link" href="http://localhost:8002/docs" target="_blank">→ Swagger</a>
          <a class="link" href="http://localhost:8002/health" target="_blank">→ Health</a>
        </div>
      </div>
      <div class="card">
        <h3>Data Service</h3>
        <div class="port">localhost:8001</div>
        <p>GraphQL sobre dataset CSV de e-commerce. NLP con Claude API (Anthropic). Requiere Bearer token.</p>
        <span class="badge badge-green">activo</span>
        <div class="links">
          <a class="link" href="http://localhost:8001/graphql" target="_blank">→ GraphQL Playground</a>
          <a class="link" href="http://localhost:8001/stats" target="_blank">→ Dataset Stats</a>
          <a class="link" href="http://localhost:8001/health" target="_blank">→ Health</a>
        </div>
      </div>
      <div class="card">
        <h3>Docs Service</h3>
        <div class="port">localhost:8000</div>
        <p>Swagger UI unificado con specs de Auth y Data Service. Ejemplos reales del dataset.</p>
        <span class="badge badge-green">activo</span>
        <div class="links">
          <a class="link" href="/docs" target="_blank">→ Swagger Unificado</a>
          <a class="link" href="/health" target="_blank">→ Health</a>
        </div>
      </div>
    </div>

    <div class="flow">
      <h2>Flujo de autenticación</h2>
      <div class="steps">
        <div class="step">POST /token<br><small>client_id + client_secret</small></div>
        <div class="arrow">→</div>
        <div class="step">JWT Bearer token<br><small>válido 30 min</small></div>
        <div class="arrow">→</div>
        <div class="step">Authorization header<br><small>Bearer &lt;token&gt;</small></div>
        <div class="arrow">→</div>
        <div class="step">POST /graphql<br>POST /nlp</div>
      </div>
    </div>

    <div class="footer">
      Stack: FastAPI · Strawberry · Claude API · python-jose · Pydantic v2 · pandas · Docker
      &nbsp;|&nbsp;
      <a href="/docs">Swagger Docs</a>
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok", "service": "docs_service"}
