# Architecture Advisor Agent — Design-Stage Reviewable Proposal

**Project:** Field service Work Orders  
**Target environment:** Dev  
**Proposal status:** Draft for review and human approval  
**Source status:** Based on supplied intake documents and the approved Requirements Agent summary. The technical requirements document is marked **Draft**, so this proposal should be treated as a design recommendation, not implementation authorization.

---

## 1. Executive summary

I recommend a **mobile-first, offline-capable field execution architecture** with:

- **Ionic 8 + Angular 18** client for technician handhelds and planner browser access
- **Python 3.12 + FastAPI** backend on **Azure App Service**
- **Azure SQL Database** as the transactional system for field execution records
- **Azure Blob Storage** for photos and signatures, with immutability applied for closed orders
- **Integration adapter** for enterprise asset management and inventory APIs
- **Microsoft Foundry + Microsoft Agent Framework** for diagnostic assistance
- **Azure API Management** as the mandatory gateway for all model traffic
- **Microsoft Entra ID + Intune-compliant device enforcement**
- **Idempotent sync and immutable closure design** to satisfy offline and audit requirements

This architecture aligns well with the stated constraints:
- intermittent connectivity
- immutable completion records
- advisory-only AI assistance
- upstream systems remaining system of record for assets/work orders and inventory

---

## 2. Architecture recommendation

## 2.1 Proposed logical architecture

```text
Managed Technician Device / Planner Browser
        |
        v
Ionic + Angular Client
- Queue
- Asset detail
- Service log
- Completion/sign-off
- Local offline store
- Sync engine
        |
        v
FastAPI Work Order API (Azure App Service)
- AuthN/AuthZ
- Work order state transitions
- Service entries
- Parts usage
- Completion workflow
- Evidence metadata
- Sync/idempotency
- Audit trail
        |
        +-----------------------> Azure SQL Database
        |                         - execution record
        |                         - sync state
        |                         - audit/event tables
        |
        +-----------------------> Azure Blob Storage
        |                         - photos
        |                         - signatures
        |                         - immutable evidence after closure
        |
        +-----------------------> Integration Adapter
        |                         - EAM read/write
        |                         - Inventory movement API
        |                         - retry/backoff/idempotency
        |
        +-----------------------> APIM
                                  |
                                  v
                         Microsoft Foundry / Agent Framework
                         - fault triage agent
                         - troubleshooting retrieval agent
```

---

## 2.2 Architectural style

Recommended style:

- **Layered service architecture** for core transaction processing
- **Task-based sync model** for offline-first mobile behavior
- **Integration façade/adapter pattern** for upstream systems
- **Event/audit recording** for tamper-evident closure and traceability
- **Human-in-the-loop agent workflow** for diagnostics

Why this fits:
- business rules are concentrated in one API boundary
- upstream contract volatility is isolated in the adapter
- offline sync can be implemented without exposing internal DB semantics to clients
- immutable closure can be enforced centrally

---

## 3. Key design decisions

## 3.1 Decision summary

1. **Use Azure SQL Database** for transactional consistency
2. **Use local offline store on device with sync queue**
3. **Treat closure as a one-way state transition**
4. **Store evidence binaries in Blob Storage, metadata in SQL**
5. **Use idempotency keys for all sync mutations and inventory movements**
6. **Route all model traffic through APIM**
7. **Keep AI advisory-only; no autonomous operational actions**
8. **Use managed identity for service-to-service integrations where supported**
9. **Separate internal domain contracts from upstream system contracts**
10. **Use append-only audit/event records for critical state changes**

---

## 4. Proposed ADRs

## ADR-001 — Transactional store for field execution record

**Status:** Proposed  
**Decision:** Use **Azure SQL Database** as the system of record for field execution data owned by this solution.

**Context:**
- service entries, parts lines, signatures, meter readings, and closure records are relational
- closure requires consistency across multiple entities
- immutable completion record needs strong transactional guarantees

**Consequences:**
- simpler enforcement of business invariants
- easier reporting and audit joins
- requires careful sync conflict handling for offline clients

---

## ADR-002 — Offline-first mobile synchronization

**Status:** Proposed  
**Decision:** Implement a **client-side durable offline store** with an outbound sync queue and server-side idempotent mutation processing.

**Context:**
- site wireless coverage is intermittent
- technicians must continue work while offline
- duplicate submission risk is high after reconnect

**Consequences:**
- improved resilience and technician productivity
- more complex client sync logic
- requires mutation IDs, versioning, and replay-safe APIs

---

## ADR-003 — Immutable closure model

**Status:** Proposed  
**Decision:** Once a work order reaches **Closed**, execution content becomes read-only and a tamper-evident completion record is generated.

**Context:**
- requirements state closed orders must produce an immutable audit record
- attachments and notes become read-only after closure
- evidence must be retained for policy duration

**Consequences:**
- corrections require controlled post-close exception workflow, not direct edits
- simplifies audit posture
- requires explicit handling for failed close attempts and discrepancy cases

---

## ADR-004 — Evidence storage separation

**Status:** Proposed  
**Decision:** Store photos and signature images in **Azure Blob Storage** and store only metadata, hashes, and references in SQL.

**Context:**
- evidence files are binary and may be large
- retention and immutability requirements apply
- SQL should remain optimized for transactional metadata

**Consequences:**
- better scalability and storage economics
- requires integrity checks and lifecycle controls
- closure workflow must finalize evidence references before immutability

---

## ADR-005 — AI gateway enforcement

**Status:** Proposed  
**Decision:** All model and agent traffic must traverse **Azure API Management** before reaching Microsoft Foundry.

**Context:**
- project constraints require APIM as the single enforcement point
- need quotas, observability, policy enforcement, and content safety

**Consequences:**
- centralized governance and telemetry
- additional dependency in diagnostic path
- diagnostics must degrade gracefully if APIM or model path is unavailable

---

## ADR-006 — Human approval in diagnostics workflow

**Status:** Proposed, pending clarification  
**Decision:** Agent output is **advisory only** and must pass through a human approval/review step before being presented as actionable guidance.

**Context:**
- supplied documents indicate a human approval step
- wording is ambiguous about whether the reviewer is the technician, senior engineer, or another role

**Consequences:**
- safer operational use of AI
- requires explicit UX and workflow design
- product owner must clarify reviewer identity and SLA

**Open question:** Who performs the approval step?

---

## 5. Domain model recommendation

## 5.1 Core entities

Recommended core entities:

- **Technician**
- **WorkOrder**
- **WorkOrderAssignment**
- **AssetSnapshot**
- **FaultCodeSnapshot**
- **ServiceEntry**
- **LabourEntry**
- **PartUsage**
- **InventoryMovementRequest**
- **Attachment**
- **SignatureCapture**
- **MeterReading**
- **CompletionRecord**
- **Discrepancy**
- **SyncOperation**
- **AuditEvent**
- **TroubleshootingSession**
- **EscalationRequest**

## 5.2 Ownership boundaries

### Owned by this solution
- service execution record
- labour logs
- parts usage logs
- evidence metadata
- completion record
- sync state
- audit events
- troubleshooting interaction history

### Referenced from upstream systems
- asset master
- work order master/dispatch source
- inventory stock source
- planner-facing dispatch truth

This separation is important because the requirements explicitly state upstream systems remain system of record.

---

## 6. Data model proposal

## 6.1 Relational schema outline

### `work_orders`
- `work_order_id` (PK)
- `external_work_order_id`
- `asset_id`
- `assigned_technician_id`
- `status` (`Assigned`, `InProgress`, `PendingReassign`, `ClosureBlocked`, `Closed`)
- `sla_risk`
- `asset_criticality`
- `location`
- `version_no`
- `accepted_at`
- `closed_at`
- `is_stale_upstream_data`
- `created_at`
- `updated_at`

### `work_order_assignments`
- `assignment_id` (PK)
- `work_order_id` (FK)
- `from_technician_id`
- `to_technician_id`
- `action_type` (`Assigned`, `Accepted`, `Reassigned`)
- `reason`
- `acted_by`
- `acted_at`

### `asset_snapshots`
- `snapshot_id` (PK)
- `work_order_id` (FK)
- `asset_id`
- `asset_type`
- `location`
- `snapshot_payload_json`
- `source_timestamp`
- `is_stale`

### `fault_code_snapshots`
- `fault_snapshot_id` (PK)
- `work_order_id` (FK)
- `fault_code`
- `description`
- `severity`
- `source_timestamp`

### `service_entries`
- `service_entry_id` (PK)
- `work_order_id` (FK)
- `technician_id`
- `notes`
- `started_at`
- `ended_at`
- `created_offline_at`
- `sync_status`
- `client_mutation_id`
- `created_at`

### `labour_entries`
- `labour_entry_id` (PK)
- `service_entry_id` (FK)
- `minutes_worked`
- `labour_code`
- `created_at`

### `part_usage`
- `part_usage_id` (PK)
- `service_entry_id` (FK)
- `part_id`
- `quantity`
- `uom`
- `inventory_status`
- `inventory_idempotency_key`
- `substitute_part_id`
- `created_at`

### `attachments`
- `attachment_id` (PK)
- `work_order_id` (FK)
- `service_entry_id` (nullable FK)
- `blob_uri`
- `blob_version_id`
- `content_hash`
- `media_type`
- `capture_mode` (`Photo`, `Signature`)
- `uploaded_at`
- `captured_offline_at`
- `is_read_only`
- `created_at`

### `meter_readings`
- `meter_reading_id` (PK)
- `work_order_id` (FK)
- `reading_type`
- `reading_value`
- `unit`
- `tolerance_min`
- `tolerance_max`
- `is_within_tolerance`
- `captured_at`

### `completion_records`
- `completion_record_id` (PK)
- `work_order_id` (FK, unique)
- `technician_id`
- `site_contact_name`
- `site_contact_signature_attachment_id`
- `technician_signature_attachment_id` (optional if required later)
- `completion_payload_json`
- `record_hash`
- `retention_until`
- `closed_at`
- `immutable_at`

### `discrepancies`
- `discrepancy_id` (PK)
- `work_order_id` (FK)
- `discrepancy_type`
- `details`
- `status`
- `raised_at`
- `resolved_at`

### `sync_operations`
- `sync_operation_id` (PK)
- `client_mutation_id` (unique)
- `device_id`
- `technician_id`
- `work_order_id`
- `operation_type`
- `request_hash`
- `processing_status`
- `response_code`
- `processed_at`

### `audit_events`
- `audit_event_id` (PK)
- `entity_type`
- `entity_id`
- `event_type`
- `actor_id`
- `event_timestamp`
- `event_payload_json`
- `event_hash`
- `correlation_id`

### `troubleshooting_sessions`
- `session_id` (PK)
- `work_order_id` (FK)
- `fault_code`
- `agent_request_ref`
- `guidance_payload_json`
- `review_status`
- `reviewed_by`
- `reviewed_at`
- `outcome`

---

## 7. API contract proposal

## 7.1 API design principles

- RESTful resource model for core work-order operations
- explicit command endpoints for state transitions
- optimistic concurrency using version or ETag
- idempotency required for mutation endpoints
- sync-friendly payloads with client mutation IDs
- no direct client access to upstream systems or model endpoints

---

## 7.2 Core endpoints

## Work order queue

### `GET /api/v1/work-orders`
Query params:
- `assignedTo=me`
- `status=open`
- `since=<timestamp>`
- `pageSize=50`

Response:
```json
{
  "items": [
    {
      "workOrderId": "WO-1001",
      "externalWorkOrderId": "EAM-77821",
      "status": "Assigned",
      "slaRisk": 1,
      "assetCriticality": 2,
      "assetId": "AST-9001",
      "assetType": "Pump",
      "location": "Plant A / Line 2",
      "summary": "High vibration alarm",
      "isStaleUpstreamData": false,
      "version": 7,
      "updatedAt": "2026-08-27T09:15:00Z"
    }
  ],
  "serverTime": "2026-08-27T09:15:05Z"
}
```

Sorting should default to:
1. SLA risk
2. asset criticality
3. updated timestamp

---

## Work order detail

### `GET /api/v1/work-orders/{workOrderId}`

Response includes:
- work order summary
- asset snapshot
- active fault codes
- recent service history
- current service entries
- attachment metadata
- closure eligibility flags

---

## Accept work order

### `POST /api/v1/work-orders/{workOrderId}/accept`

Request:
```json
{
  "clientMutationId": "8f9f2f3d-4f7d-4d4c-9f1d-0a1f7f6d1111",
  "expectedVersion": 7,
  "acceptedAt": "2026-08-27T09:16:00Z"
}
```

Response:
```json
{
  "workOrderId": "WO-1001",
  "status": "InProgress",
  "version": 8,
  "processed": true
}
```

Rules:
- idempotent on `clientMutationId`
- reject if already closed
- reject version conflict with `409 Conflict`

---

## Reassign work order

### `POST /api/v1/work-orders/{workOrderId}/reassign`

Request:
```json
{
  "clientMutationId": "4a2c0d9e-0a9b-4c7d-b1d2-2e2f11112222",
  "expectedVersion": 8,
  "toTechnicianId": "TECH-204",
  "reason": "Specialist electrical certification required"
}
```

---

## Add service entry

### `POST /api/v1/work-orders/{workOrderId}/service-entries`

Request:
```json
{
  "clientMutationId": "1b3f0d66-8d1d-4f0d-9f0e-333344445555",
  "startedAt": "2026-08-27T09:20:00Z",
  "endedAt": "2026-08-27T10:05:00Z",
  "notes": "Inspected motor housing and replaced worn coupling insert.",
  "labour": [
    {
      "minutesWorked": 45,
      "labourCode": "MECH_STD"
    }
  ],
  "parts": [
    {
      "partId": "PART-778",
      "quantity": 1,
      "uom": "EA",
      "scanSource": "barcode"
    }
  ],
  "capturedOfflineAt": "2026-08-27T10:05:10Z"
}
```

Response should include:
- created service entry ID
- inventory movement submission status
- substitute/back-order options if blocked

---

## Attachment upload flow

Recommended two-step pattern:

### `POST /api/v1/work-orders/{workOrderId}/attachments/initiate`
Returns pre-authorized upload details or server-mediated upload token.

### `POST /api/v1/work-orders/{workOrderId}/attachments/complete`
Registers metadata:
```json
{
  "clientMutationId": "att-123",
  "blobReference": "blob://...",
  "contentHash": "sha256-...",
  "mediaType": "image/jpeg",
  "captureMode": "Photo",
  "capturedOfflineAt": "2026-08-27T10:10:00Z"
}
```

For Dev, a simpler server-upload pattern is acceptable if security and size constraints are manageable.

---

## Diagnostics guidance

### `POST /api/v1/work-orders/{workOrderId}/diagnostics/guidance`

Request:
```json
{
  "faultCode": "FC-2009",
  "assetId": "AST-9001",
  "includeRecentHistory": true
}
```

Response:
```json
{
  "sessionId": "TS-10001",
  "reviewStatus": "PendingApproval",
  "guidance": [
    {
      "stepNo": 1,
      "text": "Inspect coupling alignment and wear pattern."
    },
    {
      "stepNo": 2,
      "text": "Check vibration sensor mounting and cable integrity."
    }
  ],
  "disclaimer": "Advisory guidance only. Technician approval required before action."
}
```

If approval is by another role, response should omit actionable presentation until approved.

---

## Close work order

### `POST /api/v1/work-orders/{workOrderId}/close`

Request:
```json
{
  "clientMutationId": "close-999",
  "expectedVersion": 12,
  "siteContact": {
    "name": "Jordan Smith",
    "signatureAttachmentId": "ATT-5001"
  },
  "meterReadings": [
    {
      "readingType": "Hours",
      "value": 1820.4,
      "unit": "h"
    }
  ],
  "closureNotes": "Returned asset to service. Test run normal."
}
```

Response:
```json
{
  "workOrderId": "WO-1001",
  "status": "Closed",
  "completionRecordId": "CR-7001",
  "closedAt": "2026-08-27T10:30:00Z",
  "immutable": true
}
```

Validation:
- at least one service entry exists
- site-contact signature required
- meter reading required
- tolerance check must pass
- all pending evidence references finalized
- no unresolved sync dependency for closure-critical data

---

## Sync endpoint

### `POST /api/v1/sync/batch`

Purpose:
- submit queued offline mutations
- receive per-item results
- reduce chattiness on reconnect

Request:
```json
{
  "deviceId": "DEV-001",
  "operations": [
    {
      "clientMutationId": "op-1",
      "operationType": "AcceptWorkOrder",
      "payload": { "...": "..." }
    },
    {
      "clientMutationId": "op-2",
      "operationType": "CreateServiceEntry",
      "payload": { "...": "..." }
    }
  ]
}
```

Response:
```json
{
  "results": [
    {
      "clientMutationId": "op-1",
      "status": "Processed",
      "httpStatus": 200
    },
    {
      "clientMutationId": "op-2",
      "status": "Conflict",
      "httpStatus": 409,
      "message": "Version mismatch"
    }
  ]
}
```

---

## 8. Integration contract recommendations

## 8.1 Enterprise asset management integration

Use adapter-owned contracts, not direct pass-through.

### Read operations
- get assigned work orders
- get asset details
- get active fault codes
- get recent service history
- update assignment/acceptance status where required

### Failure behavior
As stated in source documents, recommended behavior:
- 2-second timeout target
- 3 retries with exponential backoff and jitter
- if exhausted, serve cached asset/work-order snapshot marked stale
- raise integration alert

### Design note
Cache should be **bounded and explicit**, not silently authoritative.

---

## 8.2 Inventory movement integration

Critical requirement: decrement stock **once and only once**.

Recommended contract fields:
- `inventoryMovementId`
- `partId`
- `quantity`
- `uom`
- `workOrderId`
- `serviceEntryId`
- `idempotencyKey`
- `technicianId`
- `timestamp`

Failure handling:
- if out of stock, block entry finalization or mark as unresolved with substitute/back-order options per business rule
- retries must reuse same idempotency key
- API responses should distinguish:
  - accepted
  - duplicate already processed
  - insufficient stock
  - substitute available
  - back-order available

---

## 9. Sync and offline architecture

## 9.1 Client-side recommendation

Use a durable local store with:
- assigned work orders
- accepted work order details
- asset snapshots
- service entries pending sync
- attachment upload queue
- sync operation log
- last successful sync watermark

Likely implementation options in Ionic/Angular:
- IndexedDB via a supported abstraction
- encrypted local storage for sensitive metadata where feasible
- background sync when connectivity returns

## 9.2 Sync rules

1. Every mutation gets a `clientMutationId`
2. Server stores processed mutation IDs
3. Mutations are replay-safe
4. Closure is blocked until required local artifacts are uploaded and registered
5. Conflicts return explicit resolution instructions
6. Read models can be stale; write models must be validated on sync

## 9.3 Conflict strategy

Recommended strategy by operation:

- **Accept work order:** optimistic concurrency; reject if already accepted/closed by another actor
- **Reassign:** reject on stale version; user must refresh
- **Service entry creation:** allow append if work order still open
- **Attachment registration:** idempotent by content hash + mutation ID
- **Close work order:** strict validation; reject if any prerequisite changed

---

## 10. Security architecture

## 10.1 Identity and access

Recommended controls:
- Entra ID authentication
- Conditional Access requiring Intune-compliant managed devices
- role-based authorization:
  - Technician
  - Planner
  - Senior Engineer
  - Support/Admin
- least-privilege API scopes
- managed identity for backend-to-backend calls where supported

## 10.2 Data protection

- TLS in transit
- encryption at rest for SQL and Blob
- avoid storing unnecessary PII in mobile cache
- signatures and evidence treated as sensitive records
- content hashes for evidence integrity verification
- immutable storage policy applied after closure finalization

## 10.3 API protections

- APIM in front of model traffic
- rate limiting and quotas
- request/response logging with redaction
- schema validation where practical
- anti-replay/idempotency enforcement for mutation endpoints

---

## 11. Threat model considerations

Below is a reviewable STRIDE-style summary.

## 11.1 Spoofing
Threats:
- stolen technician credentials
- unauthorized device access
- forged service-to-service identity

Mitigations:
- Entra ID MFA
- Intune-compliant device enforcement
- managed identity for services
- short-lived tokens
- device/session revocation procedures

## 11.2 Tampering
Threats:
- offline data manipulation on device
- evidence file replacement
- post-closure record edits
- duplicate inventory decrements through replay

Mitigations:
- signed/idempotent sync operations
- server-side validation of all business rules
- evidence content hashing
- immutable completion record
- append-only audit events
- blob immutability after closure

## 11.3 Repudiation
Threats:
- technician disputes acceptance, reassignment, or closure actions
- inability to prove evidence lineage

Mitigations:
- actor/timestamp/correlation audit trail
- immutable closure record hash
- attachment metadata with capture/upload timestamps
- audit event retention aligned to policy

## 11.4 Information disclosure
Threats:
- cached asset/work-order data exposed on lost device
- photos/signatures leaked
- sensitive prompts or model outputs logged unsafely

Mitigations:
- managed devices
- local data minimization
- encrypted storage where possible
- log redaction
- APIM policy controls
- role-based access checks on every API call

## 11.5 Denial of service
Threats:
- upstream EAM/inventory outages
- APIM/model path degradation
- sync storm after connectivity restoration

Mitigations:
- cached stale reads for non-destructive views
- retry with backoff/jitter
- batch sync endpoint
- queue throttling
- graceful degradation for diagnostics

## 11.6 Elevation of privilege
Threats:
- technician accessing planner/admin functions
- agent workflow bypassing human review
- direct access to storage or upstream APIs

Mitigations:
- role-based authorization
- explicit workflow state checks
- no direct client access to upstream systems
- no direct model endpoint access outside APIM
- storage access mediated by backend or tightly scoped upload mechanism

---

## 12. AI/agent architecture considerations

## 12.1 Recommended workflow

1. Work Order API gathers fault code and relevant context
2. Request sent through APIM
3. Microsoft Agent Framework orchestrates:
   - fault triage
   - troubleshooting retrieval
4. Guidance returned as advisory content
5. Human review/approval step enforced
6. Guidance and outcome logged in troubleshooting session

## 12.2 Guardrails

- no direct actuation
- no automatic work-order state changes from agent output
- no direct inventory updates from agent output
- prompt inputs should be minimized to required operational context
- outputs should be labeled as advisory
- failures must not block core work-order execution

## 12.3 Open design clarification

The source documents conflict slightly on who approves suggested action before it reaches the technician. This must be resolved before implementation.

---

## 13. Non-functional architecture alignment

## Performance
Target:
- queue and asset detail under 2 seconds over site network

Recommendations:
- precomputed queue projection
- indexed SQL queries on assignee/status/sort fields
- bounded payloads
- cache recent asset snapshots
- lazy-load non-critical history/details

## Availability
Target:
- 99.9% during shift hours

Recommendations:
- App Service Premium v3
- zone redundancy in primary region
- warm standby in paired region
- health probes and alerting
- dependency-aware degradation

## Offline
Target:
- full offline capture and sync on reconnect

Recommendations:
- local durable store
- sync queue
- replay-safe APIs
- attachment upload queue
- explicit sync status in UI

## Accessibility
Target:
- WCAG 2.1 AA and glove/low-light usability

Recommendations:
- large touch targets
- high contrast mode
- offline-safe form validation
- minimal typing
- barcode/camera-first interactions

---

## 14. Observability and operational design

Recommended telemetry:

### Application telemetry
- API latency
- endpoint error rates
- sync queue processing times
- conflict rates
- closure validation failures
- inventory duplicate-prevention events

### Integration telemetry
- EAM timeout/retry counts
- inventory API timeout/retry counts
- stale cache serves
- alert generation counts

### AI telemetry
- APIM request counts
- model latency
- content safety policy hits
- guidance approval/rejection rates
- fallback/degraded-mode usage

### Audit telemetry
- work-order state transitions
- reassignment reasons
- closure record generation
- evidence immutability application success/failure

---

## 15. Reviewable technical implementation plan

## Phase 1 — Foundation
- establish repo structure and environment configuration
- define OpenAPI contract for core work-order endpoints
- create SQL schema baseline
- set up Blob storage conventions
- define auth model and role claims
- define sync/idempotency framework

## Phase 2 — Core work-order flow
- queue endpoint and sorting logic
- work-order detail endpoint
- accept/reassign commands
- planner visibility hooks
- stale-data indicators and cache handling

## Phase 3 — Service log and parts
- service entry creation
- labour and parts persistence
- inventory adapter with idempotency keys
- out-of-stock/substitute/back-order response model

## Phase 4 — Evidence and offline
- attachment capture and upload flow
- offline queue and reconnect sync
- attachment metadata registration
- read-only enforcement after closure

## Phase 5 — Completion and immutability
- meter reading validation
- signature capture registration
- close workflow transaction
- completion record generation and hashing
- immutability policy application for evidence

## Phase 6 — Diagnostics assistance
- APIM-routed model integration
- Agent Framework orchestration
- troubleshooting session persistence
- human approval workflow
- degraded-mode behavior

## Phase 7 — Hardening
- threat mitigation validation
- performance tuning
- accessibility review
- audit/reporting validation
- operational dashboards and alerts

---

## 16. Suggested backlog items for design-to-build handoff

1. Define canonical internal work-order domain model
2. Define sync protocol and conflict semantics
3. Define idempotency standard for all mutation endpoints
4. Define closure transaction and immutable record format
5. Define evidence hashing and retention metadata model
6. Define inventory movement adapter contract
7. Define stale-cache UX and API flags
8. Define diagnostics approval workflow actor and SLA
9. Define authorization matrix by role and endpoint
10. Define audit event taxonomy and retention rules

---

## 17. Key risks and mitigations

## Risk 1 — Ambiguous diagnostics approval workflow
Impact: blocked implementation or unsafe AI UX  
Mitigation: product/security decision before build

## Risk 2 — Offline sync complexity
Impact: duplicate writes, user confusion, closure failures  
Mitigation: early sync protocol design, test harness, idempotency-first APIs

## Risk 3 — Upstream integration instability
Impact: stale data, failed dispatch updates, stock inconsistency  
Mitigation: adapter isolation, retries, stale-read UX, alerting

## Risk 4 — Immutability enforcement gaps
Impact: audit failure  
Mitigation: one-way close transaction, append-only audit, evidence hash + immutable storage

## Risk 5 — Inventory decrement duplication
Impact: stock inaccuracies  
Mitigation: mandatory idempotency key per parts line and duplicate-detection telemetry

---

## 18. Required clarifications before implementation approval

1. Who performs the diagnostics human approval step?
2. Is planner web access in scope for this release or only technician mobile?
3. Is technician signature also required, or only site-contact signature?
4. What is the authoritative meter tolerance source and rule format?
5. What is the exact retention policy expression for completion records and evidence in Dev vs production?
6. Are offline reassignment actions truly allowed, or only offline work logging on already accepted orders?
7. What post-close correction process is required if an error is discovered after closure?

---

## 19. Recommendation

**Recommend approval for design progression with clarifications**, not yet for implementation.

The proposed architecture is coherent, implementable, and aligned to the supplied constraints, especially:
- offline-first operation
- immutable closure
- upstream system-of-record boundaries
- APIM-governed AI usage through Microsoft Agent Framework

The main gating issue is the **diagnostics approval workflow ambiguity**, followed by a few policy and scope clarifications.

If useful, I can next convert this into a **formal architecture package** with:
1. ADR documents,
2. OpenAPI starter spec,
3. SQL DDL draft,
4. sequence diagrams for sync/closure/diagnostics,
5. and a traceability matrix from requirements to architecture.