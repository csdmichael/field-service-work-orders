# Requirements Agent — Plan-Stage Proposal

**Project:** Field service Work Orders  
**Target environment:** Dev  
**Status:** **Reviewable proposal — not approved and not yet executed**  
**Source artifacts:** Requirements v1.0 demo artifact, Technical Requirements v1.0 draft dated 2026-08-24, UX mockups.  
**Approved artifacts supplied:** None.

## 1. Executive summary

The proposed release is a technician-facing, mobile-first work-order execution application that enables technicians to:

1. View and prioritize assigned work orders.
2. Accept or reassign work.
3. Review asset details, fault codes, history, and guided diagnostics.
4. Capture labour, parts, photographs, and notes, including offline capture.
5. Complete work with meter readings and site-contact sign-off.
6. Produce an immutable, tamper-evident completion record retained for seven years.

The proposed implementation uses:

- **Ionic 8 / Angular 18 / TypeScript** mobile and planner-facing client.
- **Python 3.12 / FastAPI** service layer on Azure App Service.
- **Azure SQL Database** for relational execution data.
- **Azure Blob Storage** with immutability for evidence.
- **Microsoft Foundry and Microsoft Agent Framework** for assisted fault triage and troubleshooting retrieval.
- **Azure API Management** as the gateway for all model traffic.
- **Microsoft Entra ID with Intune-compliant-device conditional access**.
- **GitHub Actions** for CI/CD.

The primary delivery risks are offline synchronization, immutable closure, integration reliability, inventory idempotency, and unresolved business rules around permissions, meter tolerances, retention configuration, and reassignment.

---

# 2. Proposed traceability hierarchy

## EPIC-01 — Field Service Work Orders

**Business outcome:**  
As a maintenance operations team, we want technicians to receive, diagnose, and complete work orders from a handheld device so that asset downtime is reduced and every intervention leaves a complete, auditable record.

| Feature | Scope | Source traceability |
|---|---|---|
| FEAT-01 | Work Order Queue and Dispatch | Requirements, SCR-01, US-101–US-102 |
| FEAT-02 | Asset Detail and Diagnostics | Requirements, SCR-02, US-201–US-202 |
| FEAT-03 | Service Log and Parts | Requirements, SCR-03, US-301–US-302 |
| FEAT-04 | Completion and Sign-off | Requirements, SCR-04, US-401–US-402 |
| FEAT-NFR | Cross-cutting quality, security, offline, and operational controls | Technical Requirements and NFR section |

---

# 3. Proposed user stories and acceptance criteria

The identifiers below preserve the IDs in the requirements document. Additional acceptance criteria are proposed to make implementation and testing more explicit.

## FEAT-01 — Work Order Queue and Dispatch

### US-101 — View prioritized assigned work orders

**Story:**  
As a technician, I want to see my assigned work orders ranked by SLA risk and asset criticality so I can work my route in the right order.

**Acceptance criteria:**

1. Given open assigned work orders exist, when the queue loads, orders are sorted by:
   1. SLA risk, highest risk first.
   2. Asset criticality, highest criticality first.
2. Each queue item displays sufficient dispatch context, including work-order identifier, priority or SLA state, asset identifier, location, and current status.
3. A newly assigned work order appears in the technician’s queue within **30 seconds**, without manual refresh, when connectivity is available.
4. When the upstream work-order system is unavailable, the client displays the last synchronized queue timestamp and identifies stale data.
5. Only work orders authorized for the signed-in technician are displayed.
6. Queue loading and asset-detail rendering meet the target of **under two seconds over the site network**, subject to an agreed measurement method.

### US-102 — Accept or reassign a work order

**Story:**  
As a technician, I want to accept or reassign a work order so dispatch always reflects who is actually working it.

**Acceptance criteria:**

1. Given an unaccepted order, when the technician accepts it, the work-order status changes to **In Progress**.
2. The planner and upstream work-order system receive the status change when connectivity is available.
3. A reassignment requires a reason before submission.
4. The reassignment reason, previous assignee, new assignee, actor, and timestamp are recorded against the work order.
5. Unauthorized users cannot reassign work orders.
6. Repeated submission caused by retry or reconnect does not create duplicate transitions or audit entries.
7. If the transition cannot be synchronized, the client clearly shows the pending state and does not represent the change as confirmed by the system of record.

---

## FEAT-02 — Asset Detail and Diagnostics

### US-201 — View asset details and service history

**Story:**  
As a technician, I want to view an asset’s active fault codes and recent service events so I can diagnose without calling the plant office.

**Acceptance criteria:**

1. Given a work order for an asset, the asset view displays asset ID, type, location, and active fault codes.
2. The ten most recent service events are displayed newest first when history exists.
3. The source and last-refresh time are visible where data may be stale.
4. If the asset-management system is unavailable, a cached asset record may be shown and is marked stale.
5. Asset and work-order data are protected according to the signed-in user’s authorization.
6. The view remains available offline for an accepted order if the data was previously synchronized.

### US-202 — Use guided troubleshooting

**Story:**  
As a technician, I want guided troubleshooting steps for the reported fault so common issues resolve on the first visit.

**Acceptance criteria:**

1. Given a known fault code, matching troubleshooting steps are displayed in order.
2. Diagnostic content identifies the relevant fault code or retrieval basis.
3. Given no matching content, the application offers escalation to a senior engineer and records the gap.
4. Agent-generated or retrieved suggestions are advisory only and cannot directly operate an asset or change work-order state.
5. The workflow includes the required human approval step before a suggested action is presented as an actionable recommendation to the technician.
6. All model traffic is routed through Azure API Management.
7. Model requests and responses are handled under approved content-safety, privacy, quota, and observability policies.
8. If the agent service is unavailable, the technician can continue with available static or previously cached diagnostic content and receives a clear unavailable-state message.
9. Diagnostic outputs are traceable to the work order, fault code, agent workflow, and content source where applicable.

---

## FEAT-03 — Service Log and Parts

### US-301 — Log labour and consumed parts

**Story:**  
As a technician, I want to log labour time and the parts I used so inventory and cost reporting stay accurate.

**Acceptance criteria:**

1. The technician can enter labour time against a work order.
2. A part can be scanned or selected.
3. When a valid part log is saved, the inventory system decrements on-hand stock exactly once.
4. Each inventory movement includes an idempotency key associated with the parts line.
5. Retries, reconnects, and duplicate client submissions do not produce duplicate stock movements.
6. If the part is out of stock, the entry is blocked and the application offers the approved substitute or back-order path.
7. If inventory cannot be reached, the application does not falsely confirm stock consumption; it records a pending or failed state according to the approved offline policy.
8. The service log is auditable, including technician, timestamp, quantity, part, and work-order association.
9. Offline entries are retained locally and synchronized when connectivity returns.

### US-302 — Attach photographs and notes

**Story:**  
As a technician, I want to attach photos and notes to a work order so the record supports later warranty or dispute claims.

**Acceptance criteria:**

1. The technician can attach photographs and notes to an open work order.
2. A photograph captured offline is queued locally and uploaded when connectivity returns.
3. Upload retry is safe and does not create duplicate evidence records.
4. Upload status is visible to the technician.
5. Evidence is stored in Azure Blob Storage through the approved service boundary.
6. When an order is closed, its attachments and notes become read-only.
7. Failed uploads are retained for retry or surfaced as an exception requiring resolution before closure, according to the approved policy.
8. Evidence metadata includes work order, uploader, capture or upload time, and integrity information where required.

---

## FEAT-04 — Completion and Sign-off

### US-401 — Capture sign-off and verified meter readings

**Story:**  
As a technician, I want to capture site-contact sign-off with verified meter readings so the work order meets completion policy.

**Acceptance criteria:**

1. A work order must contain at least one service entry before closure can be requested.
2. A site-contact signature is mandatory for closure.
3. A meter reading is mandatory for closure.
4. Readings outside the approved tolerance are rejected and create a discrepancy.
5. The closure workflow clearly identifies missing, invalid, or out-of-tolerance information.
6. Closure cannot proceed while mandatory discrepancies remain unresolved or explicitly approved through the designated exception process.
7. Signature and meter-reading data are associated with the work order, technician, site contact, and timestamp.
8. The closure operation is idempotent and cannot create multiple completion records.

### US-402 — Produce an immutable completion record

**Story:**  
As a maintenance planner, I want every closed order to produce a tamper-evident record so I can answer an audit without reconstructing history.

**Acceptance criteria:**

1. When an order is closed, a timestamped completion record is created.
2. The record includes technician, site contact, parts, labour, readings, notes, attachments, closure time, and relevant work-order history.
3. The completion record is written transactionally with the closure state.
4. The record and associated evidence cannot be edited after closure.
5. Closed-order evidence is stored in an immutable Blob Storage container or equivalent approved retention control.
6. Records are retained for **seven years**, or for the period configured by the approved asset-retention policy if that policy supersedes the technical default.
7. The record supports integrity verification and audit retrieval.
8. Attempts to modify a closed order are rejected and audited.

---

# 4. Cross-cutting non-functional requirements

| ID | Requirement | Proposed verification |
|---|---|---|
| NFR-01 | Work queue and asset detail render in under two seconds over the site network | Performance test using agreed device, network, dataset, and percentile |
| NFR-02 | Service platform availability target of 99.9% during shift hours | Monitoring and availability reporting |
| NFR-03 | Accepted orders can be viewed and work can be logged offline | Device-level offline scenario tests |
| NFR-04 | Synchronization is durable, retryable, and idempotent | Reconnect, duplicate request, conflict, and failure-injection tests |
| NFR-05 | Entra ID SSO with MFA and Intune-compliant managed devices | Conditional-access and negative authorization tests |
| NFR-06 | Mobile interface conforms to WCAG 2.1 AA and supports gloves and low-light use | Accessibility audit and field usability test |
| NFR-07 | Closed records and evidence are immutable and retained for seven years | Storage-policy, modification-attempt, and audit tests |
| NFR-08 | All model traffic uses APIM with managed identity, quotas, content safety, and observability | Gateway configuration and integration tests |
| NFR-09 | App Service uses Premium v3 with zone redundancy and paired-region warm standby | Architecture and resilience validation |
| NFR-10 | CI/CD uses GitHub Actions with provenance attestation and environment protection rules | Pipeline review and deployment-control test |

---

# 5. Proposed implementation tasks

## EPIC-01 / Foundation and architecture

- **TASK-001:** Confirm domain model and ownership boundaries.
  - Work-order system of record: enterprise asset management system.
  - Inventory system of record: inventory system.
  - Execution record owner: this application.
- **TASK-002:** Define API contracts and OpenAPI schemas for queue, work order, asset, diagnostics, service entries, parts, evidence, closure, and synchronization.
- **TASK-003:** Define authorization model for technicians, planners, senior engineers, and administrators.
- **TASK-004:** Establish Azure SQL schema, migrations, audit tables, and optimistic-concurrency strategy.
- **TASK-005:** Establish Blob Storage containers, metadata model, encryption, retention, and immutability policy.
- **TASK-006:** Define correlation IDs, audit events, telemetry, alerts, and operational dashboards.
- **TASK-007:** Define Dev environment configuration and secret/managed-identity boundaries without embedding secrets in source control.

## FEAT-01 tasks

- **TASK-101:** Implement queue API and SLA-risk/criticality ordering.
- **TASK-102:** Implement Ionic queue screen based on SCR-01.
- **TASK-103:** Implement assignment, acceptance, reassignment, and reason capture.
- **TASK-104:** Implement real-time or short-interval queue refresh within the 30-second requirement.
- **TASK-105:** Implement stale-data indicators and cached queue behavior.
- **TASK-106:** Test authorization, concurrent assignment changes, and duplicate state transitions.

## FEAT-02 tasks

- **TASK-201:** Implement asset and service-history adapter.
- **TASK-202:** Implement asset detail screen based on SCR-02.
- **TASK-203:** Implement fault-code and recent-history retrieval, caching, and stale-state handling.
- **TASK-204:** Configure Foundry diagnostic and troubleshooting agents through Microsoft Agent Framework.
- **TASK-205:** Implement APIM routing, managed identity, quotas, content safety, and telemetry for model calls.
- **TASK-206:** Implement human approval gate for diagnostic recommendations.
- **TASK-207:** Implement escalation and no-match recording.
- **TASK-208:** Test agent unavailability, unsafe content, prompt/data isolation, and traceability.

## FEAT-03 tasks

- **TASK-301:** Implement service-entry and labour APIs.
- **TASK-302:** Implement parts scanning and selection.
- **TASK-303:** Implement inventory adapter with idempotency keys, retries, backoff, and reconciliation.
- **TASK-304:** Implement service-log screen based on SCR-03.
- **TASK-305:** Implement local offline store and durable synchronization queue.
- **TASK-306:** Implement photo capture, compression or size policy, upload queue, retry, and status.
- **TASK-307:** Implement notes and read-only behavior after closure.
- **TASK-308:** Test duplicate submissions, stock conflicts, offline capture, and reconnect behavior.

## FEAT-04 tasks

- **TASK-401:** Implement meter-reading validation and tolerance rules.
- **TASK-402:** Implement site-contact signature capture.
- **TASK-403:** Implement completion screen based on SCR-04.
- **TASK-404:** Implement closure transaction and concurrency controls.
- **TASK-405:** Generate completion record and integrity metadata.
- **TASK-406:** Apply Blob immutability and retention controls.
- **TASK-407:** Implement audit retrieval and integrity verification.
- **TASK-408:** Test closure failure, retry, out-of-tolerance readings, and post-closure modification attempts.

## Cross-cutting quality and delivery tasks

- **TASK-501:** Establish unit, API, integration, contract, UI, accessibility, performance, security, and resilience test suites.
- **TASK-502:** Configure GitHub Actions build, test, provenance attestation, and protected deployment stages.
- **TASK-503:** Configure App Service, SQL, Blob, APIM, monitoring, and alerting for Dev.
- **TASK-504:** Conduct device and field-network testing on managed Android handhelds.
- **TASK-505:** Conduct threat modeling and privacy review for signatures, photos, asset data, and model interactions.
- **TASK-506:** Prepare operational runbooks for synchronization failures, inventory reconciliation, evidence upload failures, and integration outages.
- **TASK-507:** Prepare data migration or initial synchronization strategy, if existing work orders must be loaded into the application.

---

# 6. Dependencies

| Dependency | Owning area | Impact |
|---|---|---|
| Enterprise asset-management REST contract and test environment | Integration Platform / EAM owner | Queue, asset details, status transitions, and history |
| Inventory movement API and stock/substitute rules | Inventory owner | Parts logging and stock accuracy |
| Work-order assignment and planner permissions | Maintenance Operations | Acceptance, reassignment, and dispatch behavior |
| SLA-risk and asset-criticality definitions | Maintenance Operations | Queue ordering |
| Meter types, units, and tolerance rules | Asset/EAM and maintenance policy owners | Closure validation |
| Site-contact identity and signature policy | Operations / Legal or compliance | Completion sign-off |
| Seven-year retention and immutability policy | Records/Compliance | Completion record and evidence storage |
| Foundry model deployments and troubleshooting content index | AI Engineering | Diagnostic assistance |
| Human approval policy for agent recommendations | AI Governance / Operations | Diagnostic workflow |
| Intune enrollment and conditional-access policy | Identity/Endpoint team | Authentication and device access |
| Dev Azure subscriptions, managed identities, and network access | Platform Operations | Environment deployment |
| UX specification details contained in mockup panels | UX owner | Screen-level implementation and accessibility |
| Approved availability and performance measurement method | Platform/Product | NFR sign-off |

---

# 7. Risks and proposed mitigations

| Risk | Severity | Mitigation / decision needed |
|---|---:|---|
| Offline synchronization may create conflicts or duplicate stock movements | High | Define operation IDs, idempotency keys, conflict rules, reconciliation UI, and failure-state semantics before implementation |
| Closure may become partially committed across SQL, Blob, and upstream systems | High | Use a transactional closure boundary, an outbox or workflow pattern, and explicit completion-record generation status |
| Technical requirements are marked **Draft**, while no approved artifacts were supplied | High | Obtain product, architecture, security, and UX approval before code-generation or implementation gates |
| Requirements document text appears truncated at the accessibility section | Medium | Retrieve and review the complete source document, especially remaining NFRs, assumptions, and out-of-scope content |
| Reassignment permissions and target-assignee selection are undefined | High | Confirm who may reassign, which users are eligible, and whether planner approval is required |
| SLA-risk ordering is not mathematically defined | Medium | Approve SLA-risk calculation, tie-breakers, and behavior when data is missing or stale |
| Meter tolerance rules are unspecified | High | Define tolerance by asset/meter type, units, precision, and discrepancy workflow |
| Inventory substitute and back-order behavior is unspecified | High | Confirm source of substitute data, reservation rules, and whether offline parts capture is permitted |
| Agent recommendations may expose sensitive operational data or produce unsafe guidance | High | Enforce APIM, content safety, grounding, human approval, auditability, and no direct actuation |
| Seven-year evidence retention may conflict with privacy or legal requirements | Medium | Obtain records-management and privacy approval for signatures, photographs, deletion holds, and access |
| 99.9% platform availability may not be achievable if upstream systems target 99.5% | High | Define service-level boundaries, degraded-mode behavior, and reporting responsibilities |
| UX mockups are image-based and detailed specifications are not available in extracted text | Medium | Obtain screen annotations, interaction states, error states, and responsive/mobile accessibility specifications |
| Device/browser support and screen sizes are unspecified | Medium | Approve supported Android versions, handheld models, planner browser versions, camera/scanner capabilities, and storage limits |

---

# 8. Open decisions and approval gates

The following decisions should be resolved before implementation approval:

1. **Requirements baseline**
   - Confirm the requirements document is complete; the supplied text ends during the accessibility section.
   - Confirm whether the technical requirements document remains draft or is approved as the architecture baseline.

2. **Dispatch and permissions**
   - Define technician versus planner permissions.
   - Confirm whether technicians can reassign directly or only request reassignment.
   - Define valid reassignment targets and approval workflow.

3. **Offline behavior**
   - Define which operations are permitted offline.
   - Define conflict resolution when an order changes upstream while offline.
   - Define whether parts consumption may be captured offline or only queued pending inventory confirmation.
   - Define behavior when the same order is edited from multiple devices.

4. **Completion policy**
   - Define meter types, units, tolerance ranges, rounding, and discrepancy approval.
   - Confirm whether closure requires successful synchronization with EAM and inventory.
   - Confirm whether failed evidence uploads block closure.

5. **AI governance**
   - Approve the diagnostic agent scope, grounding sources, model deployments, and human approval step.
   - Define what constitutes a recommendation requiring approval.
   - Confirm retention and audit requirements for prompts, responses, and retrieved content.
   - Confirm that no agent may initiate external actions or mutate system-of-record data.

6. **Security and data**
   - Confirm data classification for work orders, photographs, signatures, and asset information.
   - Confirm authorization model, audit access, and privacy requirements.
   - Confirm managed-device and conditional-access policies are available in Dev.

7. **Non-functional targets**
   - Define test conditions for the two-second performance target.
   - Define shift hours and measurement boundaries for 99.9% availability.
   - Confirm supported devices, operating systems, browsers, and low-connectivity conditions.

8. **Retention and immutability**
   - Approve seven-year retention as the default.
   - Confirm legal hold, export, audit retrieval, and deletion/expiry behavior.
   - Confirm the Azure Blob immutability policy and lock mode.

---

# 9. Proposed Definition of Ready

A story is ready for implementation when:

- Business rules and authorization are approved.
- Relevant UX states, including loading, offline, error, empty, and conflict states, are available.
- API contracts and upstream dependencies are documented.
- Test data and integration environments are available or explicitly mocked.
- Offline and idempotency behavior is specified where applicable.
- Security and privacy classification is known.
- Acceptance criteria are testable and linked to the source requirement.
- No unresolved decision can materially change the implementation approach.

# 10. Proposed Definition of Done

A story is done when:

- Implementation is complete and peer reviewed.
- Automated unit and integration tests pass.
- Relevant acceptance criteria pass in Dev.
- Accessibility, security, and offline behavior are tested where applicable.
- Telemetry, audit events, and failure handling are implemented.
- API and UX documentation are updated.
- No secrets are stored in source control.
- Evidence of test results is attached to the work item.
- Required human approval gates have been completed.

## Recommendation

Approve this as a **planning baseline only**, subject to resolution of the open decisions above. Do not authorize code generation or production-impacting integration work until the requirements, technical architecture, UX details, security controls, and AI governance decisions are formally approved.