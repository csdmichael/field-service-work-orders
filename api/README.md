# Field service Work Orders — API

FastAPI service. Owns validation, authorization, and all database access.

| Path | Purpose |
| --- | --- |
| `/health` | Liveness probe |
| `/docs` | Swagger UI |
| `/openapi.json` | OpenAPI document |
| `/api/work-orders` | Work Orders collection (GET, POST) |
| `/api/work-orders/{id}` | Single work order (GET, PATCH, DELETE) |
