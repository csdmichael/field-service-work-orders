# API contracts — Field service Work Orders

The OpenAPI document is the authoritative contract: Swagger UI at `/docs`, raw document at `/openapi.json`. This table is the summary.

| Method | Path | Purpose | Response |
| --- | --- | --- | --- |
| `GET` | `/health` | Liveness probe used by the deploy pipeline | `{"status": "ok"}` |
| `GET` | `/api/work-orders` | List work orders; `?status=` filters | `WorkOrder[]` |
| `POST` | `/api/work-orders` | Create a work order | `201` + `WorkOrder` |
| `GET` | `/api/work-orders/{id}` | Fetch one work order | `WorkOrder` or `404` |
| `PATCH` | `/api/work-orders/{id}` | Partial update | `WorkOrder` or `404` |
| `DELETE` | `/api/work-orders/{id}` | Remove a work order | `204` or `404` |

## `WorkOrder`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | integer | Server assigned |
| `title` | string | Required, 1–400 characters |
| `reference` | string | Optional, up to 200 characters |
| `status` | enum | `new`, `in-progress`, `complete` |
| `priority` | enum | `low`, `normal`, `high` |
