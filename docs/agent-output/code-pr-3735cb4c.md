## Build-Stage Code Generation Proposal (for review)

**Project:** Field Service Work Orders  
**Target env:** Dev  
**Scope of this build:** Implement the vertical slice that covers FEAT-01 (Work Order Queue & Dispatch) and FEAT-02 (Asset Detail & Diagnostics), including offline-ready Ionic UI, FastAPI endpoints, Azure SQL persistence, and diagnostics-agent integration hooks. FEAT-03/04 remain out-of-scope for this increment and will need separate build proposals.

---

### 1. Current repository state & assumptions

| Area | Observations / assumptions |
| --- | --- |
| Repo layout | Based on prior docs, expect a mono-repo with `apps/mobile` (Ionic/Angular) and `apps/api` (FastAPI). If these folders do not yet exist, this build will add them following the documented stack. |
| Data | No committed schema/scripts were referenced in the intake docs. We will introduce Alembic-managed migrations under `apps/api/migrations`. |
| Integrations | External enterprise systems (EAM, Inventory, Foundry) are not directly accessible from Dev. This build will implement provider abstractions with in-repo fakes so that local tests run deterministically. |
| Offline store | The Ionic client will rely on Capacitor Storage/SQLite + a service-worker-backed queue. We assume service worker scaffolding is already enabled; if not, we’ll add it during this build. |

If any of these assumptions conflict with the actual repo, please comment before approval so the plan can be adjusted.

---

### 2. Requirements-to-build mapping

| Requirement ID | Build deliverable |
| --- | --- |
| US-101/102 | Queue API (`GET /work-orders`, `POST /work-orders/{id}/accept`, `POST /work-orders/{id}/reassign`), Angular queue page with SLA/criticality sorting, realtime refresh & offline cache. |
| US-201 | Asset detail API (`GET /work-orders/{id}/asset`), client detail screen w/ fault codes & 10 most recent service events. |
| US-202 | Diagnostics API (`GET /work-orders/{id}/diagnostics`), Agent Framework proxy in FastAPI calling APIM, UI component for guided troubleshooting + escalation path; human-approval acknowledgement UI gate. |
| NFR performance | Server-side query optimization (indexed views, SQLAlchemy query hints) plus client-side skeleton states and local-cache hydration within <2s target. |
| Offline | Indexed queue snapshot & work-order detail cache stored locally; background sync service ensures 30-second update window when online. |
| Security | All API routes protected via Entra-issued JWTs (validated via MSAL library on client + FastAPI dependency). |

---

### 3. Proposed implementation plan

#### 3.1 FastAPI service (`apps/api`)

1. **Domain models & schemas**
   - `apps/api/models/work_order.py`: SQLAlchemy models for `WorkOrder`, `Asset`, `ServiceEvent`, `DispatchSubscription`.
   - `apps/api/schemas/work_order.py`: Pydantic models for queue responses, accept/reassign payloads, diagnostics responses.
   - Add Alembic migration `apps/api/migrations/versions/<timestamp>_work_order_baseline.py`.

2. **Repository layer**
   - `apps/api/repositories/work_orders.py`: query helpers (ordered queue, asset summary, event history).
   - `apps/api/repositories/diagnostics.py`: stub to orchestrate diagnostics-agent call and persistence of guidance usage logs.

3. **Service layer**
   - `apps/api/services/distribution.py`: handles SLA / criticality ranking, new dispatch fan-out (SignalR/websocket or Azure Web PubSub stub).
   - `apps/api/services/diagnostics_agent.py`: wraps APIM call to Foundry/MAF, enforces “human approval” state machine and logs failures without blocking.

4. **Routers**
   - `apps/api/routers/work_orders.py`: REST routes for queue load, accept, reassign.
   - `apps/api/routers/asset_detail.py`: asset + service history endpoint.
   - `apps/api/routers/diagnostics.py`: returns ordered troubleshooting steps, handles “no guidance” escalation stub.

5. **Integration + infra**
   - `apps/api/clients/eam.py`: managed-identity client stub for enterprise asset management (with retry policy + stale markers).
   - `apps/api/clients/apim.py`: shared APIM client (requests/azure-core) to call Foundry.
   - Config additions (`apps/api/core/config.py`) for APIM base URL, MI settings, cache TTLs.

6. **Observability & guards**
   - Structured logging for state transitions.
   - Idempotency enforcement using `request_id` header for accept/reassign.

#### 3.2 Ionic/Angular client (`apps/mobile`)

1. **State management**
   - Introduce NgRx feature slice `workOrders` under `apps/mobile/src/app/store/work-orders`.
   - Actions: `loadQueue`, `loadQueueSuccess/Failure`, `acceptOrder`, `reassignOrder`, `refreshDispatch`, `loadAssetDetail`, `loadDiagnostics`.
   - Effects call new `WorkOrderApiService`.

2. **Services**
   - `WorkOrderApiService`: handles HTTP calls (via generated OpenAPI client or HttpClient).
   - `OfflineCacheService`: wraps Capacitor Preferences/SQLite for queue & detail caching.
   - `DispatchRefreshService`: background task (Capacitor BackgroundRunner) to poll/subscribe every ≤30s when online; uses offline snapshot when offline.

3. **UI components/pages**
   - `pages/work-order-queue`: list, SLA badges, criticality tags, immediate reflection of new dispatch.
   - `components/dispatch-card`: displays asset/location context.
   - `pages/work-order-detail`: includes asset summary, service history timeline, diagnostics panel with step tracker & escalation CTA.
   - `components/approval-banner`: enforces human-approval acknowledgement before actionable diagnostics guidance is shown.

4. **Offline & UX glue**
   - Display stale-banner when data served from cache due to EAM outage.
   - Show skeleton loaders to meet perceived performance requirement.

5. **Styling & accessibility**
   - Ensure WCAG 2.1 AA contrast for badges, large touch targets for gloves.

#### 3.3 Shared artifacts

- **OpenAPI contract** generated from FastAPI via `scripts/generate_openapi.sh`, committed under `contracts/work-order-api.json`.
- **API client**: use `openapi-typescript-codegen` to generate `apps/mobile/src/app/api/generated`.

---

### 4. Testing strategy

| Layer | Tests |
| --- | --- |
| FastAPI unit | `tests/unit/test_work_order_service.py`: queue ordering logic, accept/reassign idempotency, diagnostics fallback. |
| FastAPI integration | `tests/integration/test_work_order_routes.py`: API requests against ephemeral SQLite, verifying JWT auth dependency and stale-flag behavior. |
| Diagnostics client | Mock APIM responses incl. error states; ensure human-approval gate is enforced. |
| Angular unit | Component specs for queue list, detail page, diagnostics component. |
| Angular NgRx | Reducer/effects tests ensuring offline cache hydration and refresh scheduling. |
| E2E smoke (optional this build) | Cypress or Playwright test hitting mocked API to confirm queue render < 2 seconds w/ stubbed data. |

All new tests will run under GitHub Actions workflows:
- `ci-api.yml` for FastAPI (pytest + mypy + black/isort).
- `ci-mobile.yml` for Ionic (npm test + eslint + build).

---

### 5. File-level change plan (initial)

```
apps/
  api/
    core/config.py               # + new settings
    clients/apim.py              # new
    clients/eam.py               # new stub
    models/work_order.py         # new
    repositories/work_orders.py  # new
    repositories/diagnostics.py  # new
    routers/work_orders.py       # new
    routers/asset_detail.py      # new
    routers/diagnostics.py       # new
    services/distribution.py     # new
    services/diagnostics_agent.py# new
    schemas/work_order.py        # new
    migrations/versions/*baseline_work_orders.py
    tests/unit/test_work_order_service.py
    tests/integration/test_work_order_routes.py
    tests/integration/test_diagnostics_agent.py
  mobile/
    src/app/api/generated/*      # OpenAPI-generated client
    src/app/services/work-order-api.service.ts
    src/app/services/offline-cache.service.ts
    src/app/services/dispatch-refresh.service.ts
    src/app/store/work-orders/actions.ts
    src/app/store/work-orders/reducer.ts
    src/app/store/work-orders/effects.ts
    src/app/store/work-orders/selectors.ts
    src/app/pages/work-order-queue/work-order-queue.page.ts/html/scss/spec.ts
    src/app/components/dispatch-card/*
    src/app/pages/work-order-detail/work-order-detail.page.ts/html/scss/spec.ts
    src/app/components/diagnostics-panel/*
    src/app/components/approval-banner/*
    src/theme/tokens.scss        # new badge styles if needed
  contracts/
    work-order-api.json          # OpenAPI export
scripts/
  generate_openapi.sh            # helper script
.github/workflows/
  ci-api.yml                     # updated or new
  ci-mobile.yml                  # updated or new
```

---

### 6. Risks, constraints, and open questions

1. **Human approval definition for diagnostics** – Requirements mention “workflow pauses for technician approval before suggested action reaches the technician,” which conflicts with “suggestions are advisory to the technician.” Need clarification: is the technician the approver, or must a supervisor approve before the tech sees guidance?
2. **Realtime dispatch updates** – Is Azure Web PubSub (or SignalR Service) mandated, or is 30-second polling acceptable for Dev? Plan assumes polling for this increment, upgradeable later.
3. **Offline data volume** – Need limit/retention guidance for cached service history (currently planning top 10 entries only).
4. **Identity integration** – Dev environment may not yet have Entra ID app registration; propose feature-flag-enabled mock JWT validation for local testing until credentials are provisioned.
5. **Diagnostics content source** – Need endpoint or index ID for Foundry retrieval agent; placeholder config keys will be added.

Please confirm/clarify these before implementation approval.

---

### 7. Review & next steps

- **Artifacts produced:** This proposal (build-stage) is ready for human review. No source code has been generated yet.
- **Upon approval:** we will implement according to the plan, ensuring traceable commits, unit tests, and code-review guidance per developer instructions.
- **Approval gate:** Awaiting confirmation on assumptions and open questions plus go/no-go for FEAT-01/02 scope.

Let me know if any adjustments are needed before coding begins.