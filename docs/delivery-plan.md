# Delivery plan — Field service Work Orders

Sprints are two weeks. Each sprint closes with a demo and an approval gate.

| Sprint | Focus | Exit criteria |
| --- | --- | --- |
| Sprint 1 | Foundation: repo, pipelines, schema | CI green, API deployed |
| Sprint 2 | Core scope | Approved user stories delivered |
| Sprint 3 | Hardening and release | Tests pass, release gate approved |

## Approved scope

- **Domain models & schemas**
- `apps/api/models/work_order.py`: SQLAlchemy models for `WorkOrder`, `Asset`, `ServiceEvent`, `DispatchSubscription`.
- `apps/api/schemas/work_order.py`: Pydantic models for queue responses, accept/reassign payloads, diagnostics responses.
- Add Alembic migration `apps/api/migrations/versions/<timestamp>_work_order_baseline.py`.
- **Repository layer**
- `apps/api/repositories/work_orders.py`: query helpers (ordered queue, asset summary, event history).
- `apps/api/repositories/diagnostics.py`: stub to orchestrate diagnostics-agent call and persistence of guidance usage logs.
- **Service layer**
- `apps/api/services/distribution.py`: handles SLA / criticality ranking, new dispatch fan-out (SignalR/websocket or Azure Web PubSub stub).
- `apps/api/services/diagnostics_agent.py`: wraps APIM call to Foundry/MAF, enforces “human approval” state machine and logs failures without blocking.
- **Routers**
- `apps/api/routers/work_orders.py`: REST routes for queue load, accept, reassign.
