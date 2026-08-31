# Architecture Advisor Agent Proposal: Design Stage Review  
**Project:** Field Service Work Orders  
**Target Environment:** Dev  
**Version:** 1.0 (Reviewable Proposal)

---

## 1. Architecture Overview

### 1.1 Solution Context
- **Purpose:** Technician mobile app for receiving, diagnosing, logging, and completing work orders, with traceability and document management across Azure DevOps and SharePoint.
- **Scope:** Technician-facing mobile experience only (queue, asset detail, service log, completion/sign-off).
- **Upstream Systems:** Enterprise Asset Management (EAM), Inventory, Azure DevOps, SharePoint.
- **Key Constraints:**  
  - Intermittent connectivity (offline-first, robust sync)
  - Immutable completion records
  - Managed device and Entra ID SSO
  - All model/agent operations via Microsoft Agent Framework and Azure API Management (APIM)

### 1.2 High-Level Architecture Diagram (Textual)
```
[Technician Mobile (Ionic/Angular)]
      |
      v
[FastAPI Service Layer (Azure App Service)]
      |
      |---[Azure SQL Database] (Work orders, logs, completion records)
      |---[Azure Blob Storage] (Photos, signatures, immutable evidence)
      |---[Integration Adapter]
              |---[EAM System (REST)]
              |---[Inventory System (REST)]
      |---[APIM]---[Microsoft Agent Framework (Foundry)]
```

---

## 2. Architecture Decision Records (ADRs)

### ADR-001: Technology Stack
- **Frontend:** Angular 18 + Ionic 8 (TypeScript)
- **Backend:** Python 3.12 + FastAPI
- **Database:** Azure SQL Database (strongly relational, transactional)
- **Evidence Store:** Azure Blob Storage (immutable containers)
- **Agentic Operations:** Microsoft Agent Framework via APIM
- **Identity:** Entra ID SSO, Intune-compliant devices only
- **CI/CD:** GitHub Actions (build provenance, environment protections)
- **Hosting:** Azure App Service (Premium v3, zone redundant, warm standby)

**Rationale:**  
- Stack aligns with platform standards and requirements for offline, native device features, and transactional consistency.

---

### ADR-002: Offline-First & Synchronization
- **Pattern:** Service worker-backed offline store in the mobile client; sync queue for deferred operations.
- **Sync:** Idempotent, transactional sync logic in FastAPI service; retries and conflict resolution.
- **Failure Handling:** Serve cached data, mark stale, raise alerts on integration failures.

**Rationale:**  
- Ensures technicians can work without connectivity and data integrity is preserved.

---

### ADR-003: Immutable Completion Records
- **Pattern:** On work order closure, write a tamper-evident, immutable record to Azure SQL and evidence to Blob Storage (immutable containers).
- **Retention:** 7 years (per policy).
- **Access:** Read-only after closure.

**Rationale:**  
- Supports auditability and compliance.

---

### ADR-004: Agentic Workflow Integration
- **Pattern:** All model/agent calls (fault triage, troubleshooting) routed via APIM to Microsoft Agent Framework (Foundry).
- **Human-in-the-loop:** Agent suggestions are advisory only; technician approval required before action.

**Rationale:**  
- Centralized enforcement, observability, and safety for AI/agent operations.

---

## 3. Data and API Contracts

### 3.1 API Surface (FastAPI)
- **/workorders**: List, accept, reassign, update status (GET/POST/PATCH)
- **/assets/{id}**: Asset detail, fault codes, history (GET)
- **/service-log**: Log labor, parts, photos, notes (POST)
- **/completion**: Meter readings, signatures, close order (POST)
- **/sync**: Offline data sync (POST/GET)
- **/agent/diagnostics**: Fault triage, troubleshooting (POST via APIM)

**Authentication:**  
- All endpoints require Entra ID JWT, validated via Azure AD middleware.

**Idempotency:**  
- Write endpoints require idempotency keys (for offline retry safety).

**Sample Data Contract (Work Order):**
```json
{
  "id": "WO-123456",
  "assetId": "ASSET-7890",
  "status": "In Progress",
  "slaRisk": "High",
  "criticality": "A",
  "assignedTo": "user@company.com",
  "serviceEntries": [ ... ],
  "attachments": [ ... ]
}
```

**Blob Storage Contract:**  
- Container per work order, immutable after closure.
- Metadata: work order ID, technician, timestamp, hash.

---

## 4. Threat Model Considerations

### 4.1 Authentication & Authorization
- Entra ID SSO with MFA, device compliance enforced via Intune.
- Role-based access: Technician, Planner, Admin.

### 4.2 Data Integrity & Immutability
- Completion records and evidence are write-once; enforced by database constraints and Blob immutability policies.

### 4.3 Offline Risks
- Local data is encrypted at rest.
- Sync logic prevents replay, duplication, or data loss.

### 4.4 API & Integration Security
- All external API calls use managed identity and OAuth2.
- APIM enforces quotas, content safety, and logging for all agent/model calls.

### 4.5 Privacy & Compliance
- Evidence (photos, signatures) stored per retention policy, access logged.
- No PII beyond operational necessity.

---

## 5. Implementable Technical Plan

### 5.1 Component Breakdown

| Component                | Owner                | Stack/Service            | Key Responsibilities                                |
|--------------------------|----------------------|--------------------------|-----------------------------------------------------|
| Mobile Client            | Field Apps Team      | Ionic 8, Angular 18      | UI, offline store, sync, device integration         |
| Work Order API           | Field Apps Team      | FastAPI, Python 3.12     | Business logic, validation, sync, API contracts     |
| Integration Adapter      | Integration Platform | FastAPI, Python 3.12     | EAM/inventory mapping, retries, idempotency         |
| Agentic Workflow         | AI Engineering       | Foundry, Agent Framework | Diagnostics, troubleshooting, human-in-loop         |
| Evidence Store           | Platform Ops         | Azure Blob Storage       | Immutable storage, retention, access control        |

### 5.2 Sequence of Implementation

1. **Set up Azure resources:** App Service, SQL, Blob Storage, APIM, Entra ID integration.
2. **Develop FastAPI backend:**  
   - Define OpenAPI contracts, implement endpoints, enforce idempotency.
   - Integrate with EAM/Inventory via adapters.
3. **Develop mobile client:**  
   - Implement offline store, sync logic, UI per UX mockups.
   - Integrate device camera, barcode, signature capture.
4. **Implement agentic workflow:**  
   - Route diagnostics/troubleshooting via APIM to Agent Framework.
   - Enforce human-in-the-loop.
5. **Configure evidence storage:**  
   - Set up immutable containers, retention, and access policies.
6. **CI/CD pipeline:**  
   - GitHub Actions for build, test, deploy with environment protections.
7. **Security hardening:**  
   - Entra ID SSO, device compliance, API security, logging.
8. **Testing:**  
   - Unit, integration, offline/online sync, security, accessibility.
9. **Documentation & handoff:**  
   - API docs, runbooks, traceability matrix.

---

## 6. Review Checklist

- [x] Stack and component boundaries align with requirements and constraints.
- [x] API and data contracts defined for all major flows.
- [x] Threat model addresses offline, immutability, agentic workflow, and integration risks.
- [x] Technical plan is actionable and sequenced for parallel team execution.
- [x] All model and system-of-record operations routed via Microsoft Agent Framework and APIM.
- [x] No external system changes assumed without tool-verified output.

---

## 7. Open Questions / Approval Gates

- Confirm EAM and Inventory API schemas for integration adapter mapping.
- Validate Blob Storage immutability policy with compliance/legal.
- Approve retention and access policy for evidence.
- Confirm agentic workflow review/approval step with field operations.

---

**End of Proposal — Ready for review and human approval.**