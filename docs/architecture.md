# Architecture — Field Service Work Orders

## Tiers

| Tier | Folder | Responsibility |
| --- | --- | --- |
| Web client | `ui/` | Rendering and user interaction |
| Service | `api/` | Validation, authorization, data access |
| Database | `db/` | Schema and forward-only migrations |

## Decisions

- The UI never connects to the database; all access flows through the API.
- Migrations are forward-only so every environment shares one history.
- Secrets come from environment variables or managed identity, never source.
