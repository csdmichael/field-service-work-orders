## Code Generation Agent — Build-Stage Proposal  
**Project:** Field Service Work Orders  
**Environment:** Dev  
**Status:** Reviewable proposal (not yet implemented)  
**Source inputs:** Requirements v1.0, Technical Requirements v1.0, UX mockups, Requirements-Agent summary.

---

### 1. Scope confirmation
| Feature | Stories | Build scope this cycle |
| --- | --- | --- |
| FEAT‑01 Work Order Queue & Dispatch | US‑101, US‑102 | Implement prioritized queue API + mobile view, accept/reassign actions, real-time/near-real-time refresh messaging. |
| FEAT‑02 Asset Detail & Diagnostics | US‑201, US‑202 | Asset detail endpoint, cached/offline view, diagnostics integration scaffold via Microsoft Agent Framework + APIM. |
| FEAT‑03 Service Log & Parts | US‑301, US‑302 | Service entry persistence, part usage with inventory adapter, attachment upload pipeline with offline queueing. |
| FEAT‑04 Completion & Sign-off | US‑401, US‑402 | Closure validation workflow, immutable completion record + blob evidence sealing. |
| FEAT‑NFR | N/A | Offline store durability, Entra authentication hooks, performance budget checks, audit logging. |

---

### 2. Proposed source changes

#### 2.1 FastAPI service (`api/`)

| Area | Planned modifications |
| --- | --- |
| **Routing & Schemas** | Introduce versioned router `api/v1/work_orders.py` exposing: `GET /work-orders` (sorted queue), `POST /work-orders/{id}/accept`, `POST /work-orders/{id}/reassign`, `GET /work-orders/{id}` (asset detail + history), `POST /work-orders/{id}/service-log`, `POST /work-orders/{id}/attachments`, `POST /work-orders/{id}/complete`. Add Pydantic models mirroring acceptance criteria (sorting fields, reassignment audit payload, diagnostics metadata, meter readings with tolerance window). |
| **Domain services** | Create `services/work_orders.py` handling state transitions with idempotent tokens, queue freshness timestamps, offline-aware sync flags. Add `services/diagnostics_agent.py` calling Microsoft Agent Framework through APIM (feature-flagged, retries, human-in-the-loop requirement). |
| **Data access** | Extend SQLAlchemy models: `WorkOrder`, `ServiceEntry`, `PartUsage`, `Attachment`, `CompletionRecord`, with audit columns (`created_by`, `modified_by`, `staged_changes`). Stored procedures/transactions to guarantee single decrement per parts line and immutable completion record (row-level version locking). |
| **Integration adapters** | Build `clients/asset_management.py` (managed identity auth, cache fallback) and `clients/inventory.py` (idempotency key per part usage). Implement resilience policies per technical constraints. |
| **Attachments & evidence** | Add `storage/blob_client.py` for Azure Blob interactions, ensure immutable container toggle once `CompletionRecord` exists. |
| **Security & validation** | Enforce Entra-scoped claims for technician ID and permissions. Introduce dependency that injects device-compliance information (stubbed for Dev). |
| **Observability** | Structured logging for state transitions, queue latency metrics, diagnostics-agent usage metrics (per-user quotas). |

#### 2.2 Mobile client (Angular/Ionic under `mobile/`)

| Area | Planned modifications |
| --- | --- |
| **Feature modules** | Add `work-orders` module containing screens SCR‑01 through SCR‑04 with routing guards requiring authenticated technician profile. Components: `WorkOrderQueuePage`, `AssetDetailPage`, `ServiceLogPage`, `CompletionPage`. |
| **State management** | Introduce NgRx (or existing store) slices: `queue`, `assetDetail`, `serviceLog`, `sync`. Effects coordinate API calls, offline queueing, and push updates (SignalR/WebSocket or polling fallback to meet 30‑second SLA). |
| **Offline persistence** | Service Worker + Ionic Storage adapters to cache accepted orders, service logs, attachments metadata. Implement conflict resolution markers when sync pending. |
| **Diagnostics UI** | Panel displaying fault code, steps, escalation CTA when content missing (records gap). |
| **Service log & inventory** | Parts selector integrates barcode/camera plugin; out-of-stock validation blocks save and suggests substitute/backorder. |
| **Attachments** | Camera/gallery picker with offline queue; background uploader handles retry and marks read-only after closure. |
| **Completion flow** | Dual signature capture (technician + site contact), meter reading inputs with tolerance validation, summary review before POST `/complete`. |
| **Accessibility & performance** | Enforce WCAG 2.1 AA styles, large touch targets, skeleton loaders to meet <2s render target. |

#### 2.3 Shared / infrastructure

- **Database migrations** under `infrastructure/db/migrations/` creating/altering tables noted above plus indexes for SLA risk + criticality sorting.
- **Configuration**: environment variables for APIM endpoint, Foundry agent IDs, Blob containers, tolerance thresholds, offline cache TTL.
- **CI updates**: GitHub Actions workflow to run backend unit tests (pytest), frontend tests (Jest + Cypress component tests), linting, and DB migration check.

---

### 3. Test strategy

| Layer | Tests to add (non-exhaustive) |
| --- | --- |
| **Backend unit tests (`api/tests/`)** | Sorting order logic (US‑101), acceptance/reassignment transitions including audit fields (US‑102), asset detail fallback to cache (US‑201), diagnostics agent branching (US‑202), service log stock decrement idempotency + out-of-stock block (US‑301), attachment queue & immutability toggle (US‑302), closure validation for signatures/meter tolerance + immutability enforcement (US‑401/402). |
| **Integration tests** | Simulated inventory adapter with retry + idempotency, Blob immutability after closure, diagnostics agent APIM contract (mocked). |
| **Frontend unit tests (`mobile/src/app/.../*.spec.ts`)** | Queue selector sorts/respects permissions, service log form validations, offline queue state indicators, completion form tolerance blocking. |
| **E2E / instrumentation** | Cypress or Playwright flows for: queue refresh, accept/reassign, asset diagnostics display, service log with barcode scan mock, photo capture offline -> sync, completion path with dual signature. |
| **Performance checks** | Automated Lighthouse or Ionic capacitor instrumentation verifying <2s render for queue + asset detail with mocked data. |

---

### 4. Risks & mitigations
1. **Offline conflict handling**: implement per-record sync status + idempotent transition tokens to prevent duplicate state changes.
2. **Diagnostics agent latency**: wrap agent calls with timeout + fallback messaging; ensure UI doesn’t block critical path.
3. **Immutable completion enforcement**: DB transaction plus Blob legal hold to prevent edits; add monitoring for unauthorized write attempts.
4. **Inventory consistency**: idempotency keys plus reconciliation job for stuck “pending” entries.
5. **Attachment storage cost**: lifecycle management for drafts, immutability only on closure.

---

### 5. Code-review checklist (to be used once code is ready)

1. **Traceability**: Every change references corresponding user story ID and acceptance criteria.
2. **Security**: Verify Entra claim checks on every endpoint/component, no secrets committed, managed identity only.
3. **Offline behavior**: Ensure caches mark stale timestamps and UI indicates pending sync.
4. **Idempotency & concurrency**: Review transaction scopes, idempotency tokens, and retry logic.
5. **Diagnostics agent**: Confirm APIM usage, logging, human-in-the-loop gate present.
6. **Evidence immutability**: Blob container configuration toggled on closure; attachments read-only afterward.
7. **Performance budgets**: API queries have appropriate indexes; frontend uses pagination/virtual scroll as needed.
8. **Testing**: New/updated tests cover success/failure paths; CI workflow updated accordingly.
9. **Accessibility**: Components include ARIA labels, large touch targets, dark-mode contrast.
10. **Error handling & telemetry**: Meaningful errors bubbled to UI; structured logs/metrics instrumented.

---

### 6. Approvals required before implementation
- Confirm tolerance configuration source (per asset class) and escalation workflow owner.
- Validate diagnostics agent integration details (Foundry project IDs, content index availability).
- Sign-off on database schema additions and immutability retention policy mapping.
- UX approval for offline/latency indicators and reassignment reason capture flow.

---

This proposal is ready for stakeholder review. No code has been executed or merged. Please provide approval, clarifications, or change requests before the implementation phase begins.