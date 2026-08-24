# API contracts — Field Service Work Orders

The OpenAPI document is the authoritative contract: Swagger UI at `/docs`, raw document
at `/openapi.json`. This table is the summary.

| Method | Path | Purpose | Response |
| --- | --- | --- | --- |
| `GET` | `/health` | Liveness probe used by the deploy pipeline | `{"status": "ok"}` |
| `GET` | `/api/work-items` | List work items; `?status=` filters | `WorkItem[]` |
| `POST` | `/api/work-items` | Create a work item | `201` + `WorkItem` |
| `GET` | `/api/work-items/{id}` | Fetch one work item | `WorkItem` or `404` |
| `PATCH` | `/api/work-items/{id}` | Partial update | `WorkItem` or `404` |
| `DELETE` | `/api/work-items/{id}` | Remove a work item | `204` or `404` |

## `WorkItem`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | integer | Server assigned |
| `title` | string | Required, 1–400 characters |
| `location` | string | Optional |
| `status` | enum | `new`, `in-progress`, `complete` |
| `priority` | enum | `low`, `normal`, `high` |
