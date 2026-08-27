# Architecture Advisor Agent — Design-Stage Reviewable Proposal

**Project:** Field service Work Orders  
**Target environment:** Dev  
**Status:** **Reviewable proposal — design output only; no systems changed**  
**Basis:** Intake requirements, technical requirements, UX mockups, and supplied Requirements Agent summary.

---

## 1. Executive summary

This proposal translates the approved planning inputs into a reviewable architecture package for the design stage.

### Recommended architecture
A mobile-first field execution solution with:

- **Ionic 8 + Angular 18** client for technician handhelds and planner browser access
- **Python 3.12 + FastAPI** service layer on **Azure App Service**
- **Azure SQL Database** as the transactional system for field execution records
- **Azure Blob Storage** for photos and signatures, with immutability after closure
- **Integration adapter** for enterprise asset management and inventory APIs
- **Microsoft Foundry + Microsoft Agent Framework** for diagnostic assistance
- **Azure API Management** as the mandatory gateway for all model traffic
- **Microsoft Entra ID + Intune-compliant device conditional access**
- **GitHub Actions** for CI/CD

### Architectural position
The solution should be designed around four dominant constraints:

1. **Offline-first technician workflow**
2. **Idempotent synchronization and inventory updates**
3. **Immutable, tamper-evident closure record**
4. **Human-in-the-loop AI assistance only**

### Key design decisions
- Use **Azure SQL** rather than Cosmos DB because closure, parts, service entries, and audit records require strong relational consistency.
- Treat the **enterprise asset management system** as system of record for assets and work orders, and the **inventory system** as system of record for stock.
- Treat this solution as the **system of record for field execution evidence and completion record**.
- Enforce **append-only audit and immutable closure semantics** in both data model and API behavior.
- Route all AI/model requests through **APIM**, with no direct client-to-model path.

### Primary risks
- Sync conflict handling for offline edits
- Duplicate or partial inventory decrements
- Closure race conditions
- Evidence upload consistency when offline
- Ambiguity in some business rules not fully specified in source material

---

## 2. Scope and assumptions

## In scope
- Technician work queue
- Accept/reassign workflow
- Asset detail and diagnostics
- Service log, parts, photos, notes
- Completion with meter reading and signatures
- Immutable completion record
- AI-assisted troubleshooting retrieval and triage
- Offline capture and reconnect sync

## Out of scope
Per source requirements:
- Planning and scheduling
- Payroll
- Enterprise asset management ownership
- Inventory ownership
- Autonomous AI actions on assets

## Assumptions requiring confirmation
1. Planner browser view uses the same backend APIs and authorization model.
2. Reassignment is permitted only to authorized dispatch/planner roles or a constrained technician workflow.
3. Meter-reading tolerance rules come from configuration, not hardcoded logic.
4. Signature capture is image-based, not PKI-backed digital signing.
5. “Tamper-evident” means immutable record + audit metadata + evidence immutability, not blockchain or external notarization.
6. Offline mode applies to **accepted orders only**, consistent with technical requirements.
7. Dev environment may use reduced retention/immutability settings for cost and operability, while preserving design parity.

---

## 3. Proposed logical architecture

## 3.1 Context view

**Actors and systems**
- Technician on managed Android device
- Planner in browser
- Work Order API
- Integration Adapter
- Azure SQL Database
- Azure Blob Storage
- Enterprise Asset Management system
- Inventory system
- Diagnostics Agent Workflow in Foundry
- APIM for model traffic
- Entra ID for identity

## 3.2 Component model

### A. Mobile/Web Client
Responsibilities:
- Render queue, asset detail, service log, completion flow
- Maintain local offline store
- Maintain sync queue
- Capture photos, notes, signatures, meter readings
- Display stale/pending/synced states clearly

Key design notes:
- Use local persistence suitable for Ionic offline patterns
- Separate UI view models from sync entities
- Maintain per-entity sync status and conflict markers

### B. Work Order API
Responsibilities:
- Canonical business API for client
- State transitions and business rule enforcement
- Service entry and parts line management
- Completion workflow orchestration
- Evidence metadata registration
- Audit event creation
- AI workflow invocation through APIM/Foundry path

Key design notes:
- FastAPI with typed contracts
- Idempotency support for mutating operations
- Optimistic concurrency for updates before closure
- Hard block edits after closure

### C. Integration Adapter
Responsibilities:
- Translate internal contracts to external EAM and inventory APIs
- Retry/backoff/jitter
- Idempotency for stock movement
- Cache asset/work-order snapshots where allowed
- Raise integration alerts/events

Key design notes:
- Keep external schemas isolated from core domain model
- Use adapter boundary to prevent upstream contract leakage into client

### D. SQL Data Store
Responsibilities:
- Transactional persistence for work execution domain
- Audit trail
- Sync state support
- Immutable completion record metadata

### E. Blob Evidence Store
Responsibilities:
- Store photos and signatures
- Enforce immutability after closure
- Retention management
- Evidence integrity metadata

### F. Diagnostics Agent Workflow
Responsibilities:
- Fault triage ranking
- Troubleshooting retrieval
- Human review checkpoint before technician sees actionable guidance if policy requires
- Logging of prompt/response metadata through governed path

### G. APIM
Responsibilities:
- Single ingress for model traffic
- Managed identity auth
- Quotas, safety policies, observability
- Request/response policy enforcement

---

## 4. Domain model recommendations

## 4.1 Core entities

### WorkOrder
Represents technician-facing execution of an upstream work order.

Suggested fields:
- `workOrderId` (internal UUID)
- `externalWorkOrderId`
- `assetId`
- `assignedTechnicianId`
- `status` (`Assigned`, `InProgress`, `PendingSync`, `Completed`, `Closed`, `Reassigned`)
- `slaRisk`
- `assetCriticality`
- `location`
- `acceptedAt`
- `closedAt`
- `version`
- `lastSyncedAt`
- `sourceSnapshotTimestamp`

### AssetSnapshot
Cached asset context for offline use.

Fields:
- `assetId`
- `assetType`
- `location`
- `activeFaultCodes`
- `snapshotCapturedAt`
- `staleAfter`
- `sourceSystem`

### ServiceEntry
Fields:
- `serviceEntryId`
- `workOrderId`
- `technicianId`
- `laborMinutes`
- `notes`
- `startedAt`
- `endedAt`
- `createdAt`
- `isOfflineCaptured`

### PartUsage
Fields:
- `partUsageId`
- `workOrderId`
- `serviceEntryId`
- `partNumber`
- `quantity`
- `uom`
- `inventoryMovementStatus`
- `inventoryIdempotencyKey`
- `substitutionOffered`
- `createdAt`

### Attachment
Fields:
- `attachmentId`
- `workOrderId`
- `type` (`Photo`, `Signature`)
- `blobUri`
- `contentHash`
- `capturedAt`
- `uploadedAt`
- `uploadStatus`
- `capturedOffline`

### MeterReading
Fields:
- `meterReadingId`
- `workOrderId`
- `readingType`
- `value`
- `unit`
- `capturedAt`
- `withinTolerance`
- `toleranceRuleId`

### CompletionRecord
Immutable closure artifact.

Fields:
- `completionRecordId`
- `workOrderId`
- `technicianId`
- `siteContactName`
- `siteContactSignatureAttachmentId`
- `technicianSignatureAttachmentId` if required
- `meterReadingSummary`
- `partsSummary`
- `serviceSummary`
- `closedAt`
- `retentionPolicyId`
- `recordHash`
- `immutableFrom`

### AuditEvent
Append-only event log.

Fields:
- `auditEventId`
- `workOrderId`
- `eventType`
- `actorId`
- `actorType`
- `occurredAt`
- `correlationId`
- `idempotencyKey`
- `beforeJson`
- `afterJson`

## 4.2 State model

Recommended work order lifecycle:

- `Assigned`
- `Accepted`
- `InProgress`
- `PendingClosure`
- `Closed`
- `Reassigned`
- `ClosureBlocked`

Notes:
- Upstream mapping may differ; internal state machine should map explicitly.
- Once `Closed`, all mutable child entities become read-only.
- `PendingSync` should be a client sync state, not necessarily a business state.

---

## 5. Data architecture and storage design

## 5.1 Azure SQL schema recommendation

Suggested schema groups:

### Operational schema
- `work_orders`
- `service_entries`
- `part_usage`
- `meter_readings`
- `attachments`
- `asset_snapshots`

### Audit/immutability schema
- `completion_records`
- `audit_events`
- `state_transitions`

### Integration schema
- `outbound_messages`
- `integration_attempts`
- `sync_checkpoints`

### Reference/config schema
- `fault_code_mappings`
- `troubleshooting_content_refs`
- `meter_tolerance_rules`
- `retention_policies`

## 5.2 Immutability design
For closed orders:
- Disallow update/delete in API layer
- Restrict DB permissions to prevent accidental mutation
- Use append-only audit events
- Persist a final `completion_record`
- Lock evidence blobs via immutability policy
- Store content hashes for evidence and completion summary

## 5.3 Evidence storage design
Blob path convention:
`/work-orders/{workOrderId}/{attachmentType}/{attachmentId}`

Metadata:
- `workOrderId`
- `attachmentType`
- `capturedAt`
- `contentHash`
- `uploadedBy`
- `closureState`

Recommendation:
- Use separate container classes for mutable-in-flight and immutable-closed evidence, or enforce policy transition at closure.

---

## 6. API contract recommendations

Below are reviewable contract proposals, not final generated OpenAPI.

## 6.1 Client-facing API surface

### Queue and dispatch
- `GET /api/v1/work-orders?assignee=me&status=open`
- `POST /api/v1/work-orders/{id}/accept`
- `POST /api/v1/work-orders/{id}/reassign`

### Asset and diagnostics
- `GET /api/v1/work-orders/{id}`
- `GET /api/v1/work-orders/{id}/asset`
- `GET /api/v1/work-orders/{id}/history`
- `POST /api/v1/work-orders/{id}/diagnostics/query`

### Service log and parts
- `POST /api/v1/work-orders/{id}/service-entries`
- `POST /api/v1/work-orders/{id}/parts`
- `POST /api/v1/work-orders/{id}/attachments/initiate`
- `POST /api/v1/work-orders/{id}/attachments/{attachmentId}/complete`

### Completion
- `POST /api/v1/work-orders/{id}/meter-readings`
- `POST /api/v1/work-orders/{id}/closure/validate`
- `POST /api/v1/work-orders/{id}/close`
- `GET /api/v1/work-orders/{id}/completion-record`

### Sync support
- `GET /api/v1/sync/bootstrap`
- `POST /api/v1/sync/batch`
- `GET /api/v1/sync/status/{clientRequestId}`

## 6.2 API behavior requirements

All mutating endpoints should support:
- `Idempotency-Key` header
- `If-Match` or version token where relevant
- `X-Correlation-Id`

All responses should include:
- server timestamp
- entity version
- sync status where applicable

## 6.3 Example contracts

### Accept work order
`POST /api/v1/work-orders/{id}/accept`

Request:
```json
{
  "clientRequestId": "8d8e7b1a-2c4a-4e0f-a1d0-2d5d6f7a1001",
  "acceptedAt": "2026-08-27T10:15:00Z"
}
```

Response:
```json
{
  "workOrderId": "wo-123",
  "status": "InProgress",
  "acceptedAt": "2026-08-27T10:15:02Z",
  "version": 7,
  "syncState": "Confirmed"
}
```

### Reassign work order
`POST /api/v1/work-orders/{id}/reassign`

Request:
```json
{
  "newAssigneeId": "tech-456",
  "reasonCode": "SKILL_MISMATCH",
  "reasonText": "Requires certified electrical specialist",
  "clientRequestId": "f0d3f4d2-6f4f-4f6f-8d3a-0f1f2f3f4f5a"
}
```

### Add part usage
`POST /api/v1/work-orders/{id}/parts`

Request:
```json
{
  "serviceEntryId": "se-100",
  "partNumber": "P-77821",
  "quantity": 2,
  "uom": "EA",
  "scanSource": "BARCODE",
  "clientRequestId": "part-req-001"
}
```

Response:
```json
{
  "partUsageId": "pu-9001",
  "inventoryMovementStatus": "Pending",
  "inventoryIdempotencyKey": "inv-wo-123-pu-9001",
  "substitutionOptions": []
}
```

### Close work order
`POST /api/v1/work-orders/{id}/close`

Request:
```json
{
  "siteContact": {
    "name": "Jordan Smith",
    "signatureAttachmentId": "att-sign-001"
  },
  "meterReadings": [
    {
      "readingType": "HOURS",
      "value": 1245.6,
      "unit": "h"
    }
  ],
  "clientRequestId": "close-wo-123"
}
```

Response:
```json
{
  "workOrderId": "wo-123",
  "status": "Closed",
  "closedAt": "2026-08-27T11:02:14Z",
  "completionRecordId": "cr-123",
  "immutable": true,
  "retentionUntil": "2033-08-27T00:00:00Z"
}
```

## 6.4 External integration contracts

### EAM integration
Operations:
- fetch assigned work orders
- fetch asset details
- fetch recent service history
- update assignment/status where required

Requirements:
- timeout 2 seconds
- cached fallback for reads
- explicit stale-data indicator

### Inventory integration
Operations:
- reserve or validate part availability if supported
- decrement stock on confirmed usage
- query substitutes/back-order options

Requirements:
- timeout 3 seconds
- idempotency key per part usage line
- no duplicate decrement on retry

---

## 7. Offline and synchronization architecture

## 7.1 Offline-first principles
- Accepted orders must be usable offline
- Local writes are durable before UI confirmation
- Sync is asynchronous and resumable
- Server remains source of truth for final confirmation
- UI must distinguish:
  - saved locally
  - pending sync
  - synced
  - conflict
  - failed

## 7.2 Recommended sync model
Use an **operation-based sync queue**, not full-record overwrite.

Queued operations:
- accept work order
- reassign work order
- create service entry
- add part usage
- upload attachment metadata
- submit meter reading
- request closure

Each operation should carry:
- client request ID
- entity ID
- operation type
- timestamp
- idempotency key
- dependency chain if needed

## 7.3 Conflict strategy
Recommended rules:
- **Append operations** like notes, photos, service entries: merge safely
- **State transitions**: reject invalid stale transitions and return current state
- **Closure**: single-writer finalization; if already closed, return completion record
- **Reassignment/acceptance**: use version checks and clear conflict messaging

## 7.4 Attachment sync
Recommended pattern:
1. Capture file locally
2. Create local attachment record
3. On reconnect, request upload initiation
4. Upload blob
5. Confirm upload completion
6. Include attachment in closure validation

---

## 8. AI/agent architecture recommendations

## 8.1 Allowed AI role
AI is advisory only:
- rank likely causes
- retrieve troubleshooting content
- identify missing knowledge coverage
- suggest escalation

AI must not:
- execute work order changes autonomously
- close work orders
- alter inventory
- issue control commands to assets

## 8.2 Workflow design
Recommended sequence:
1. Client requests diagnostics for work order/fault code
2. Work Order API assembles minimal context
3. API calls APIM
4. APIM routes to Foundry/Microsoft Agent Framework workflow
5. Fault triage agent ranks probable causes
6. Troubleshooting retrieval agent fetches relevant content
7. Policy/human-review checkpoint applied
8. Response returned with provenance and disclaimer

## 8.3 AI contract shape
Suggested response:
```json
{
  "faultCode": "FC-201",
  "probableCauses": [
    {
      "label": "Filter blockage",
      "confidence": 0.74
    }
  ],
  "troubleshootingSteps": [
    {
      "stepNumber": 1,
      "instruction": "Inspect intake filter for obstruction.",
      "sourceRef": "KB-4432"
    }
  ],
  "escalationOffered": true,
  "advisoryOnly": true,
  "generatedAt": "2026-08-27T10:20:00Z"
}
```

## 8.4 AI governance requirements
- APIM-only routing for model traffic
- Managed identity authentication
- Prompt/response logging with redaction
- Content safety policy enforcement
- Per-user quotas
- No secrets in prompts
- Minimal necessary context only
- Human approval before any suggested action is operationalized

---

## 9. Security architecture and threat-model considerations

## 9.1 Identity and access
- Entra ID SSO
- Conditional access requiring Intune-compliant managed devices
- Role-based authorization:
  - Technician
  - Planner
  - Supervisor
  - Support/Admin
- Fine-grained checks on reassignment, closure, and evidence access

## 9.2 Data protection
- TLS in transit
- Encryption at rest for SQL and Blob
- Managed identities for service-to-service auth
- No embedded credentials in client
- Minimize PII in logs and AI prompts

## 9.3 Threat model summary using STRIDE

### Spoofing
Risks:
- stolen device/session
- forged sync requests

Mitigations:
- Entra ID + MFA
- device compliance
- token validation
- short-lived tokens
- correlation and audit trails

### Tampering
Risks:
- offline store manipulation
- evidence replacement
- closure record edits

Mitigations:
- signed/authenticated API calls
- server-side validation
- content hashes
- immutable blob policy after closure
- append-only audit events
- read-only enforcement after closure

### Repudiation
Risks:
- user denies reassignment, parts usage, or closure

Mitigations:
- audit events with actor, timestamp, correlation ID
- signature capture linkage
- immutable completion record

### Information disclosure
Risks:
- cached data exposure on device
- overbroad API responses
- prompt leakage to AI systems

Mitigations:
- encrypted local storage where supported
- least-privilege APIs
- role-based filtering
- prompt minimization and APIM governance
- log redaction

### Denial of service
Risks:
- upstream dependency outages
- sync storms after reconnect
- model quota exhaustion

Mitigations:
- backoff/jitter
- local queue throttling
- stale-cache fallback for reads
- APIM quotas
- warm standby region

### Elevation of privilege
Risks:
- technician performing planner-only actions
- bypassing closure validation

Mitigations:
- server-side authorization
- policy-based endpoint guards
- workflow validation before closure
- no client-trusted role decisions

## 9.4 Additional mobile-specific concerns
- Lost/stolen device
- Screenshot/data leakage
- Offline evidence left on device
- Rooted/jailbroken device risk

Mitigations:
- Intune controls
- device compliance
- app data wipe on unenroll where supported
- local retention minimization
- no permanent local storage after successful sync where not needed

---

## 10. Reliability, performance, and operability

## 10.1 Performance targets
From requirements:
- Queue and asset detail under 2 seconds over site network

Design implications:
- precomputed queue sort fields
- indexed SQL access paths
- asset snapshot caching
- pagination and bounded history retrieval
- async evidence upload

## 10.2 Availability
Target:
- 99.9% during shift hours

Design implications:
- App Service Premium v3
- zone redundancy
- paired-region warm standby
- health probes and alerting
- dependency-aware degradation for EAM/inventory/model services

## 10.3 Observability
Recommended telemetry:
- API latency and error rate
- sync queue depth
- offline-to-sync success rate
- duplicate idempotency suppression count
- inventory retry count
- closure validation failure reasons
- evidence upload failure rate
- AI request volume, latency, safety blocks

Use:
- correlation IDs end-to-end
- structured logs
- audit logs separate from operational logs

---

## 11. Architecture decision records

## ADR-001: Use Azure SQL Database for execution record
**Status:** Proposed  
**Decision:** Use Azure SQL Database as primary transactional store.  
**Rationale:** Strong relational consistency, transactional closure, auditability, and simpler enforcement of immutable completion semantics.  
**Consequences:** Need careful scaling and indexing; offline sync complexity remains in app layer.

## ADR-002: Use operation-based offline sync with idempotent commands
**Status:** Proposed  
**Decision:** Sync client mutations as discrete commands with idempotency keys.  
**Rationale:** Safer than record overwrite for intermittent connectivity and duplicate retries.  
**Consequences:** More sync orchestration logic; clearer audit and conflict handling.

## ADR-003: Closed work orders are immutable
**Status:** Proposed  
**Decision:** After successful closure, work order and child records become read-only; changes require compensating records, not edits.  
**Rationale:** Required for tamper-evident audit record.  
**Consequences:** Support processes must handle corrections via exceptions, not updates.

## ADR-004: Store evidence in Blob Storage with immutability after closure
**Status:** Proposed  
**Decision:** Photos and signatures stored in Blob; immutability policy applied at closure.  
**Rationale:** Cost-effective binary storage with retention support.  
**Consequences:** Need clear lifecycle for pre-closure vs post-closure evidence.

## ADR-005: Route all model traffic through APIM
**Status:** Proposed  
**Decision:** No direct Foundry/model access from client or backend bypassing APIM.  
**Rationale:** Governance, quotas, safety, observability, and policy enforcement.  
**Consequences:** APIM becomes critical dependency for AI features.

## ADR-006: AI remains advisory with human-in-the-loop
**Status:** Proposed  
**Decision:** AI may suggest diagnostics and troubleshooting only; no autonomous operational actions.  
**Rationale:** Matches requirements and safety posture.  
**Consequences:** UX must clearly label AI output as advisory.

## ADR-007: Separate integration adapter from core work order API
**Status:** Proposed  
**Decision:** External EAM/inventory contracts terminate in adapter boundary.  
**Rationale:** Reduces coupling and isolates retries/idempotency.  
**Consequences:** Additional service/component complexity, but better maintainability.

---

## 12. Implementable technical plan

## 12.1 Workstreams

### Workstream 1: API and domain foundation
- Define OpenAPI contracts
- Implement domain model and state machine
- Add idempotency middleware
- Add optimistic concurrency/versioning
- Implement audit event pipeline

### Workstream 2: Offline-capable client
- Build queue, asset detail, service log, completion screens
- Implement local store and operation queue
- Add sync status UX
- Add camera/barcode/signature capture
- Add stale-data indicators

### Workstream 3: Integration adapter
- EAM read/update adapters
- Inventory decrement/substitute flows
- Retry/backoff/jitter
- Idempotency key propagation
- Integration alerting

### Workstream 4: Evidence and closure
- Attachment initiation/upload/complete flow
- Blob metadata and hashing
- Closure validation endpoint
- Completion record generation
- Immutability policy application design

### Workstream 5: AI diagnostics
- APIM route and policies
- Foundry agent workflow
- minimal-context prompt assembly
- troubleshooting retrieval contract
- advisory UX and provenance display

### Workstream 6: Security and operations
- Entra ID authN/authZ
- managed identities
- telemetry and dashboards
- alert rules
- CI/CD pipelines and environment protections

## 12.2 Suggested delivery sequence
1. Domain model + API contracts
2. Queue + accept flow
3. Asset detail + cached snapshots
4. Service entries + parts + inventory idempotency
5. Attachments offline/upload
6. Closure validation + immutable completion record
7. AI diagnostics workflow
8. Hardening, observability, accessibility, performance

## 12.3 Definition of done for design stage
- Architecture reviewed and approved
- ADRs accepted or amended
- API contracts reviewed
- Data model reviewed
- Threat model reviewed
- Open questions assigned owners
- Delivery plan sequenced into implementation backlog

---

## 13. Testing strategy recommendations

### Functional
- Queue ordering
- accept/reassign rules
- asset detail/history retrieval
- troubleshooting retrieval
- parts decrement behavior
- closure validation and sign-off

### Offline/sync
- create/update offline then reconnect
- duplicate submission retries
- conflict resolution
- stale cache display
- attachment upload recovery

### Security
- role enforcement
- device compliance assumptions
- token validation
- unauthorized closure/reassignment attempts
- evidence access control

### Data integrity
- exactly-once inventory decrement
- immutable closure record
- read-only closed attachments/notes
- audit completeness

### Performance
- queue load under 2 seconds
- asset detail under 2 seconds
- sync throughput after reconnect surge

### Resilience
- EAM unavailable
- inventory unavailable
- APIM/model unavailable
- blob upload interruption
- SQL transient faults

---

## 14. Open issues and decisions needed

1. **Reassignment authority model**  
   Can technicians reassign directly, or only request reassignment?

2. **Closure state mapping**  
   Does upstream EAM own final “closed” state, or does this app close locally then notify upstream?

3. **Meter tolerance source**  
   Where are tolerance rules mastered and maintained?

4. **Signature requirements**  
   Is dual signature mandatory in all cases, and is technician signature also required?

5. **Retention policy in Dev**  
   Should Dev simulate 7-year retention logically without enforcing full immutable retention physically?

6. **Offline storage technology**  
   Confirm preferred Ionic local persistence approach and encryption expectations.

7. **Planner web scope**  
   Read-only visibility or full operational parity?

8. **Compensating process for post-closure corrections**  
   What is the approved exception workflow if a closed record is wrong?

9. **Knowledge source for troubleshooting**  
   Where is troubleshooting content indexed and governed?

10. **Photo/signature classification**  
    Any privacy or legal constraints beyond public demo classification?

---

## 15. Reviewable recommendation

I recommend approving this design direction with the following conditions:

- Confirm the open business-rule items in Section 14.
- Approve the ADR set, especially immutability, APIM-only AI routing, and operation-based sync.
- Proceed to detailed API specification and implementation backlog decomposition.
- Treat offline sync and closure immutability as the two highest-risk design areas and validate them early with prototypes.

If useful, I can next produce any of these as follow-on design artifacts:

1. **Detailed ADR document set**
2. **OpenAPI draft**
3. **SQL schema draft**
4. **Sequence diagrams for sync, parts decrement, and closure**
5. **Threat model table**
6. **Implementation backlog by epic/feature**