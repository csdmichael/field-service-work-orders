# Field Service Work Orders — API

FastAPI service. Owns validation, authorization, and all database access.

| Path | Purpose |
| --- | --- |
| `/health` | Liveness probe |
| `/docs` | Swagger UI |
| `/openapi.json` | OpenAPI document |
| `/api/work-items` | Work item collection (GET, POST) |
| `/api/work-items/{id}` | Single work item (GET, PATCH, DELETE) |
