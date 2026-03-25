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
    <script>
      SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
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


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok", "service": "docs_service"}
