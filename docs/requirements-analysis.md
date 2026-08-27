# Requirements Agent — Plan-Stage Proposal

**Project:** Field Service Work Orders  
**Target environment:** Dev  
**Proposal status:** Draft for review and human approval  
**Source approval status:** No approved artifacts were supplied. The technical requirements document is marked **Draft**; the requirements document is a demo artifact. This proposal does not authorize implementation or external-system changes.

## 1. Proposed delivery objective

Deliver a mobile-first technician experience that supports:

1. Receiving and prioritizing assigned work orders.
2. Viewing asset information, fault codes, service history, and troubleshooting guidance.
3. Recording labour, parts, photographs, and notes, including offline capture.
4. Completing work orders with meter readings, site-contact sign-off, and an immutable audit record.

The proposed solution uses:

- Ionic 8 / Angular 18 / TypeScript client.
- Python 3.12 / FastAPI service layer.
- Azure SQL Database for transactional work-order data.
- Azure Blob Storage with immutability for evidence.
- Enterprise asset-management integration for asset and work-order data.
- Inventory-system integration for stock movements.
- Microsoft Foundry with Microsoft Agent Framework for diagnostic assistance.
- Azure API Management for all model traffic.
- Microsoft Entra ID with Conditional Access and Intune-compliant devices.
- Azure App Service Premium v3.
- GitHub Actions with provenance attestation and environment protection.

## 2. Proposed work hierarchy

### EPIC-01 — Field Service Work Orders

**Outcome:** Maintenance technicians can receive, diagnose, execute, and close work orders from managed handheld devices while preserving an auditable execution record.

---

## 3. Features and user stories

### FEAT-01 — Work Order Queue and Dispatch

**UX trace:** SCR-01 — Work Order Queue

#### US-101 — Prioritized assigned work-order queue

**As a** technician,  
**I want** to see my assigned work orders ranked by SLA risk and asset criticality,  
**so that** I can work my route in the right order.

**Acceptance criteria**

- Given open work orders exist, when the queue loads, orders are sorted by SLA risk and then asset criticality.
- Given a new dispatch is assigned to the technician, the queue reflects it within 30 seconds without manual refresh.
- Each queue item displays sufficient context to identify the work order, including status, priority/SLA information, asset, location, and criticality.
- If the upstream work-order system is unavailable, the application displays the last cached data as stale and raises an integration alert through the service layer.
- Queue rendering meets the agreed performance target of under two seconds over the site network.

#### US-102 — Accept or reassign work order

**As a** technician,  
**I want** to accept or reassign a work order,  
**so that** dispatch reflects who is actually working it.

**Acceptance criteria**

- Given an unaccepted order, when the technician accepts it, the status changes to **In Progress**.
- The planner and upstream work-order system receive the status change.
- Given the technician reassigns an order, a reason is mandatory.
- The reassignment reason, actor, timestamp, previous assignee, and new assignee are recorded.
- Conflicting or duplicate state changes are rejected safely and surfaced to the user.
- Offline acceptance is supported for an accepted order and synchronizes idempotently when connectivity returns.

---

### FEAT-02 — Asset Detail and Diagnostics

**UX trace:** SCR-02 — Asset Detail and Diagnostics

#### US-201 — View asset details and service history

**As a** technician,  
**I want** to view an asset’s active fault codes and recent service events,  
**so that** I can diagnose without calling the plant office.

**Acceptance criteria**

- Given a work order for an asset, the application shows asset ID, type, location, and active fault codes.
- If prior service events exist, the ten most recent are listed newest first.
- Cached asset information is clearly marked stale when the asset-management system cannot be reached.
- Asset and work-order access is restricted according to the technician’s authorization.
- Asset detail renders within the agreed under-two-second target when required data is available locally or from the service layer.

#### US-202 — Guided troubleshooting

**As a** technician,  
**I want** guided troubleshooting steps for the reported fault,  
**so that** common issues resolve on the first visit.

**Acceptance criteria**

- Given a known fault code, matching troubleshooting steps are shown in the prescribed order.
- The diagnostic workflow records the fault code, retrieved guidance, technician interaction, and outcome.
- Given no matching guidance exists, escalation to a senior engineer is offered and the gap is recorded.
- Agent-generated suggestions are advisory only and cannot directly act on an asset or change system state.
- A human approval step occurs before any suggested action is presented as an actionable recommendation to the technician.
- All model traffic routes through Azure API Management.
- The workflow handles model, gateway, and content-index failures without blocking ordinary work-order execution.

**Clarification required:** The technical document says the workflow pauses for technician approval before a suggested action reaches the technician. The product owner should confirm whether this means approval by the technician, a senior engineer, or another designated reviewer.

---

### FEAT-03 — Service Log and Parts

**UX trace:** SCR-03 — Service Log and Parts

#### US-301 — Record labour and parts

**As a** technician,  
**I want** to log labour time and the parts I used,  
**so that** inventory and cost reporting remain accurate.

**Acceptance criteria**

- A part can be scanned or selected.
- When a valid service log is saved, the corresponding stock movement is submitted.
- On-hand stock is decremented once and only once.
- Each parts movement uses an idempotency key so retries cannot create duplicate deductions.
- If a part is out of stock, the entry is blocked and a substitute or back-order option is offered.
- The user can see whether a stock movement is pending, successful, or failed.
- Offline entries are durably queued and synchronized on reconnect.
- Failed synchronization does not silently discard the service entry or parts line.

#### US-302 — Attach photographs and notes

**As a** technician,  
**I want** to attach photos and notes to a work order,  
**so that** the record supports later warranty or dispute claims.

**Acceptance criteria**

- Photos can be captured from the device camera or selected through the supported mobile workflow.
- Notes and photographs can be associated with the relevant work order and service entry.
- Given a photo is attached while offline, it is queued locally and uploaded when connectivity returns.
- Upload retry is safe and does not create duplicate evidence.
- Evidence is stored in Azure Blob Storage using the approved access-control model.
- When an order is closed, attachments and notes become read-only.
- Signature images and photographic evidence are protected by the retention and immutability policy.

---

### FEAT-04 — Completion and Sign-off

**UX trace:** SCR-04 — Completion and Sign-off

#### US-401 — Capture sign-off and meter readings

**As a** technician,  
**I want** to capture site-contact sign-off with verified meter readings,  
**so that** the work order meets completion policy.

**Acceptance criteria**

- An order cannot be submitted for closure unless it contains at least one service entry.
- A site-contact signature and meter reading are mandatory before closure.
- Meter readings are validated against the configured tolerance.
- If a reading falls outside tolerance, closure is blocked and a discrepancy is raised.
- The user receives a clear explanation of missing or invalid completion data.
- Signature images and meter readings are associated with the work-order completion transaction.
- Closure is transactional: a partially completed closure cannot leave the order in an ambiguous state.

#### US-402 — Produce immutable completion record

**As a** maintenance planner,  
**I want** every closed order to produce a tamper-evident record,  
**so that** I can answer an audit without reconstructing history.

**Acceptance criteria**

- When an order is closed, a timestamped record is written containing, at minimum, technician, site contact, parts, service entries, notes, evidence references, and readings.
- The record cannot be edited through the application after closure.
- Evidence associated with the closed order is placed under the approved immutable-storage policy.
- The record includes sufficient metadata to verify its integrity and provenance.
- Records are retained for seven years, subject to confirmation of the governing asset-retention policy.
- Closure and record creation are observable and generate an alert if persistence fails.
- Repeated closure requests do not create duplicate completion records.

---

## 4. Proposed non-functional work items

### NFR-01 — Performance

- Queue and asset-detail render target: **under two seconds** over the site network.
- Define measurement conditions, payload sizes, device profile, and percentile target before test execution.
- Add client and API performance telemetry.

### NFR-02 — Availability and resilience

- Service-platform target: **99.9% during shift hours**.
- App Service Premium v3 with zone redundancy and paired-region warm standby, subject to platform approval.
- Define recovery time objective, recovery point objective, and failover operating procedure; these are not specified in the supplied documents.

### NFR-03 — Offline operation and synchronization

- Technicians can view an accepted order and log work without connectivity.
- Local data is encrypted at rest on the device.
- Sync uses durable queues, retry/backoff, conflict handling, and idempotency keys.
- The UI shows sync state, stale data, and unresolved conflicts.
- Closed orders cannot be modified through delayed offline updates.

### NFR-04 — Security and device trust

- Entra ID SSO.
- Conditional Access requires an Intune-compliant managed device.
- No OTP path is included in the current technical proposal.
- Use managed identities for service-to-service integrations.
- Enforce least-privilege authorization for technicians, planners, senior engineers, and administrators.
- Do not store client secrets in the mobile application.

### NFR-05 — Accessibility and field usability

- Target WCAG 2.1 AA.
- Support use with gloves and in low-light conditions.
- Validate touch-target sizes, contrast, focus order, error messaging, and screen-reader behavior where applicable.
- Confirm supported handheld models, screen sizes, and Android versions.

### NFR-06 — Audit, retention, and evidence integrity

- Closed work orders are immutable.
- Photographic evidence and signature images use immutable Blob containers.
- Evidence and completion records are retained for seven years, pending policy confirmation.
- Log security-relevant actions, state changes, integration events, and diagnostic-agent activity without exposing sensitive data.

### NFR-07 — AI governance

- All model traffic passes through APIM.
- Use managed identity, per-user quotas, content-safety controls, and observability.
- Agent output is advisory and must not directly operate equipment or mutate system-of-record data.
- Record model/version, prompt or request correlation metadata, retrieved sources, approval outcome, and final user-visible recommendation according to approved privacy policy.
- Establish a fallback path when the agent is unavailable.

---

## 5. Proposed implementation tasks

### Foundation and contracts

- **TASK-001:** Confirm product scope, personas, roles, supported devices, and completion policy.
- **TASK-002:** Establish domain model for work orders, assignments, assets, service entries, parts lines, evidence, signatures, discrepancies, and completion records.
- **TASK-003:** Define FastAPI OpenAPI contracts and versioning strategy.
- **TASK-004:** Define Azure SQL schema, transaction boundaries, indexes, and immutable-record model.
- **TASK-005:** Define authorization matrix for technician, planner, senior engineer, and administrative roles.
- **TASK-006:** Define error, correlation-ID, audit, and observability standards.

### Mobile client

- **TASK-010:** Implement Ionic/Angular application shell and navigation based on the four supplied screens.
- **TASK-011:** Implement SCR-01 queue, sorting, refresh/update behavior, and stale-data indicators.
- **TASK-012:** Implement SCR-02 asset detail, service history, fault-code display, and diagnostics entry point.
- **TASK-013:** Implement SCR-03 labour, parts, scanning/selection, notes, camera, and upload status.
- **TASK-014:** Implement SCR-04 meter readings, signature capture, validation, discrepancy display, and closure.
- **TASK-015:** Implement encrypted local store and durable offline synchronization queue.
- **TASK-016:** Implement conflict handling, idempotent retries, and user-visible sync status.
- **TASK-017:** Implement accessibility and field-usability refinements.

### Work-order API and database

- **TASK-020:** Implement queue and assignment APIs.
- **TASK-021:** Implement work-order state-transition rules.
- **TASK-022:** Implement asset and service-history retrieval with cache/staleness behavior.
- **TASK-023:** Implement service-entry and parts-line APIs.
- **TASK-024:** Implement transactional closure and duplicate-submission protection.
- **TASK-025:** Implement completion-record generation and audit events.
- **TASK-026:** Implement authorization, input validation, rate limits, and API telemetry.

### Integrations

- **TASK-030:** Confirm enterprise asset-management contracts, fields, identity, timeout, and availability commitments.
- **TASK-031:** Implement asset/work-order adapter with three retries, exponential backoff, jitter, and cached fallback.
- **TASK-032:** Confirm inventory movement contract and stock semantics.
- **TASK-033:** Implement idempotent inventory movement adapter with three-second timeout behavior as specified.
- **TASK-034:** Implement integration alerts, dead-letter/retry handling, reconciliation, and operational dashboards.
- **TASK-035:** Validate upstream behavior for assignment, acceptance, reassignment, closure, and stale-data scenarios.

### Evidence and retention

- **TASK-040:** Provision Blob Storage containers and managed-identity access.
- **TASK-041:** Configure immutability policy and legal/asset-retention settings.
- **TASK-042:** Implement evidence upload, retry, checksum/integrity metadata, and read-only behavior after closure.
- **TASK-043:** Implement signature-image storage and access controls.
- **TASK-044:** Test retention, immutability, deletion prevention, and authorized retrieval.

### Diagnostics agent workflow

- **TASK-050:** Confirm approved Foundry project, model deployments, content index, and data boundaries.
- **TASK-051:** Implement fault-triage and troubleshooting retrieval agents using Microsoft Agent Framework.
- **TASK-052:** Route model traffic through APIM using managed identity.
- **TASK-053:** Implement human approval gate and ensure no agent action can mutate asset or work-order state.
- **TASK-054:** Implement content-safety, quotas, telemetry, prompt-injection defenses, and failure fallback.
- **TASK-055:** Define evaluation set for fault-code matching, retrieval quality, unsafe recommendations, and unsupported-fault escalation.

### Quality and delivery

- **TASK-060:** Configure GitHub Actions build, test, security scanning, provenance attestation, and environment protection.
- **TASK-061:** Create unit, API contract, integration, mobile, offline-sync, accessibility, and end-to-end test suites.
- **TASK-062:** Execute performance testing against the under-two-second target.
- **TASK-063:** Execute resilience, failover, retry, and reconciliation testing.
- **TASK-064:** Execute security, device-compliance, authorization, and threat-model validation.
- **TASK-065:** Conduct pilot/UAT with technicians and planners.
- **TASK-066:** Prepare operational runbooks, support procedures, and release-readiness evidence.

---

## 6. Traceability summary

| Requirement source | Proposed coverage |
|---|---|
| EPIC-01 Field Service Work Orders | EPIC-01 |
| FEAT-01 Queue and Dispatch | FEAT-01, US-101, US-102, TASK-011, TASK-020–021 |
| FEAT-02 Asset Detail and Diagnostics | FEAT-02, US-201, US-202, TASK-012, TASK-022, TASK-050–055 |
| FEAT-03 Service Log and Parts | FEAT-03, US-301, US-302, TASK-013, TASK-023, TASK-032–033, TASK-040–044 |
| FEAT-04 Completion and Sign-off | FEAT-04, US-401, US-402, TASK-014, TASK-024–025, TASK-040–044 |
| SCR-01 through SCR-04 UX mockups | Corresponding feature screens and mobile-client tasks |
| Performance under two seconds | NFR-01, TASK-062 |
| 99.9% shift-hours availability | NFR-02, TASK-063 |
| Full offline capture and sync | NFR-03, TASK-015–016, TASK-061–063 |
| Entra ID, MFA/device trust | NFR-04, TASK-005, TASK-064 |
| WCAG 2.1 AA and field usability | NFR-05, TASK-017, TASK-061 |
| Seven-year immutable evidence retention | NFR-06, TASK-040–044 |
| Foundry, Agent Framework, APIM, human approval | NFR-07, TASK-050–055 |

## 7. Dependencies

| Dependency | Required decision or capability | Owner to confirm |
|---|---|---|
| Enterprise asset-management system | Work-order, assignment, asset, fault-code, service-history, and closure contracts | Integration Platform / EAM owner |
| Inventory system | Stock availability, reservation/substitution, movement, and idempotency semantics | Inventory-system owner |
| Identity platform | Entra groups, Conditional Access, Intune compliance, managed identities | Security / Identity |
| Foundry and APIM | Approved project, deployments, quotas, policies, content index, monitoring | AI Engineering / Platform |
| Retention policy | Seven-year retention and immutability/legal-hold requirements | Asset governance / Legal |
| Device estate | Supported Android handhelds, camera/scanner capabilities, OS versions | Field Operations |
| UX specification | Extractable screen behavior, validation, error states, offline indicators, and accessibility details | Product / UX |
| Availability design | RTO, RPO, warm-standby activation, and operational ownership | Platform Operations |
| Diagnostic content | Authoritative troubleshooting procedures and escalation ownership | Maintenance Engineering |

## 8. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Upstream API contracts or availability are not confirmed | Integration rework and unreliable queue/stock behavior | Complete contract discovery and consumer-driven contract tests before integration build |
| Offline conflict semantics are undefined | Duplicate movements or incorrect work-order state | Define state-transition ownership, idempotency keys, conflict rules, and reconciliation UI |
| Inventory API cannot guarantee idempotent movement | Incorrect stock balances | Require idempotency support or introduce a controlled movement ledger and reconciliation process |
| Retention/immutability policy is not finalized | Compliance and evidence-integrity failure | Obtain written policy approval before provisioning production-like retention settings |
| UX mockups are image-only and lack interaction specifications | Ambiguous implementation and UAT defects | Review annotated flows, validation rules, error states, device targets, and accessibility behavior |
| Agent recommendations are inaccurate or unsafe | Technician may follow harmful guidance | Human approval, advisory-only behavior, curated content, safety filters, evaluation set, and escalation path |
| Model or content-index outage affects diagnostics | Reduced first-visit resolution | Provide explicit unavailable state and manual troubleshooting/escalation path |
| Seven-year evidence retention increases storage and privacy exposure | Cost and data-governance risk | Confirm retention basis, encryption, access reviews, lifecycle controls, and cost estimates |
| Availability target conflicts with upstream dependencies | End-to-end target may be unattainable | Define whether the target applies to the platform alone or the complete user journey |
| Device/network conditions differ from assumptions | Poor field usability | Pilot on representative managed devices and actual plant networks |
| Requirements source is incomplete/truncated in the supplied extract | Missed requirements | Validate against complete source documents before baselining the backlog |

## 9. Open decisions required before baseline

1. Confirm whether the requirements and technical documents are approved for implementation, rather than draft/demo inputs.
2. Confirm the complete non-functional-requirements section; the supplied requirements extract ends during the security/accessibility content.
3. Define SLA-risk calculation, tie-breaking rules, and asset-criticality source.
4. Define valid work-order states and who may perform each transition.
5. Define reassignment permissions and whether planner approval is required.
6. Define meter-reading types, units, tolerances, and discrepancy workflow.
7. Identify the authoritative asset-retention policy and confirm the seven-year period.
8. Clarify the human approval point in the diagnostics workflow.
9. Confirm whether offline creation of new work orders is out of scope; the current requirement explicitly guarantees offline work on an accepted order.
10. Confirm inventory behavior for substitute and back-order options.
11. Confirm supported devices, Android versions, scanner behavior, and camera/file constraints.
12. Define availability measurement scope, shift hours, RTO, and RPO.
13. Confirm data-classification, privacy, and audit requirements for signatures, photographs, and diagnostic telemetry.
14. Provide detailed UX annotations and navigation/error-state specifications.

## 10. Proposed approval gates

### Gate A — Requirements baseline

Approval required from product owner, maintenance operations, security, and integration owners for:

- Scope and personas.
- Work-order lifecycle.
- Completion policy.
- Offline behavior.
- Retention and audit requirements.
- Open decisions listed above.

### Gate B — Architecture and integration readiness

Approval required before implementation proceeds beyond foundational scaffolding:

- API contracts.
- Identity and authorization model.
- Offline synchronization/conflict design.
- Inventory idempotency approach.
- Evidence immutability configuration.
- Agent/APIM governance design.
- Availability and disaster-recovery design.

### Gate C — Dev validation

Evidence required:

- Automated test results.
- Contract and integration test results.
- Offline and retry testing.
- Security and accessibility findings.
- Performance measurements.
- Agent evaluation results.
- No unresolved critical defects.

### Gate D — Pilot/UAT approval

Approval required from representative technicians, planners, product owner, and operational support before any broader deployment.

## Recommendation

**Proceed to requirements clarification and architecture-readiness review only.** Baseline the proposed hierarchy after the open decisions are resolved and the complete source documents, detailed UX specifications, and upstream integration contracts are confirmed. No external system or repository change has been performed.