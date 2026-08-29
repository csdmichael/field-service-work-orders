# Delivery plan — Field service Work Orders

Sprints are two weeks. Each sprint closes with a demo and an approval gate.

| Sprint | Focus | Exit criteria |
| --- | --- | --- |
| Sprint 1 | Foundation: repo, pipelines, schema | CI green, API deployed |
| Sprint 2 | Core scope | Approved user stories delivered |
| Sprint 3 | Hardening and release | Tests pass, release gate approved |

## Approved scope

- `work-order-queue` (SCR-01): Renders prioritized list, handles real-time updates, accept/reassign actions.
- `asset-detail` (SCR-02): Displays asset info, fault codes, service history, and diagnostics agent integration.
- `offline-store` service: Manages local cache, sync queue, and durability for intermittent connectivity.
- `api-client` service: Abstracts FastAPI endpoints, handles authentication (Entra ID), error handling, and retry logic.
- `WorkOrder`: id, assetId, status, slaRisk, assetCriticality, assignedTo, etc.
- `Asset`: id, type, location, faultCodes, serviceEvents[]
- `ServiceEvent`: id, date, description, technician
- `DiagnosticsResult`: faultCode, probableCauses[], troubleshootingSteps[]
- `/queue` → Work Order Queue
- `/order/:id` → Asset Detail & Diagnostics
- Durable queue for work orders and asset data.
- Sync triggers on connectivity restoration.
