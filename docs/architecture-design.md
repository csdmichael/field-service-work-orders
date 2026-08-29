Architecture Advisor Agent – Design Stage Proposal  
Field Service Work Orders – Technician Mobile App

---

## 1. Architecture Overview

### Context
A mobile-first application for field technicians, supporting work order execution, asset diagnostics, parts logging, evidence capture, and completion sign-off. The solution demonstrates traceability and document management across Azure DevOps and SharePoint, integrating with enterprise asset management and inventory systems. It must operate reliably with intermittent connectivity, enforce data immutability on closure, and route all agent/model traffic through Microsoft Agent Framework and Azure API Management.

---

## 2. Architecture Recommendations

### 2.1 Solution Architecture Diagram (Textual)

**Technician Device (Android, Intune-managed)**
↓
**Ionic 8 + Angular 18 Mobile Client**
↓
**Python 3.12 FastAPI Service Layer (Azure App Service, Premium v3)**
↓
- **Azure SQL Database:** Work orders, service logs, completion records (strongly relational, transactional consistency)
- **Azure Blob Storage:** Photos, signatures (immutable containers for closed orders)
- **Integration Adapter:** RESTful connectors to:
  - **Enterprise Asset Management System:** Asset/work order/service history (OAuth 2.0, managed identity)
  - **Inventory System:** Parts stock/movement (idempotency, managed identity)
↓
**Microsoft Agent Framework (Foundry) via Azure API Management**
- Fault triage and troubleshooting retrieval agents (APIM for authentication, quota, content safety)

---

### 2.2 Component Boundaries

| Component              | Responsibility                               | Hosting/Runtime                | Owner                |
|------------------------|----------------------------------------------|-------------------------------|----------------------|
| Mobile Client          | UI, offline store, sync queue                | Ionic/Angular, Android/Intune | Field Apps Team      |
| Work Order API         | State transitions, business rules, evidence  | FastAPI, Azure App Service    | Field Apps Team      |
| Integration Adapter    | Upstream/downstream system connectors        | FastAPI, Azure App Service    | Integration Platform |
| Diagnostics Agent      | Fault triage, troubleshooting retrieval      | Foundry, Agent Framework      | AI Engineering Team  |
| Evidence Store         | Immutable photo/signature storage            | Azure Blob Storage            | Platform Ops Team    |

---

## 3. Decision Records

### ADR-001: Technology Stack
- **Frontend:** Angular 18 + Ionic 8 (native camera/barcode, offline store)
- **Backend:** Python 3.12 FastAPI (typed models, OpenAPI contract)
- **Database:** Azure SQL Database (relational, transactional, immutable records)
- **Evidence:** Azure Blob Storage (immutable containers for closed orders)
- **Agent/AI:** Microsoft Foundry + Agent Framework, routed via Azure API Management
- **Identity:** Entra ID, conditional access, Intune device compliance
- **CI/CD:** GitHub Actions (build provenance, environment protection)

### ADR-002: Offline & Sync
- Durable offline store in mobile client (service worker-backed)
- Sync queue with idempotent operations; retries and conflict resolution
- Evidence queued locally and uploaded on reconnect

### ADR-003: Immutability & Audit
- Completion record and evidence are immutable post-closure (Azure SQL, Blob Storage policies)
- Tamper-evident record includes technician, site contact, parts, readings, timestamps

### ADR-004: Integration
- Managed identity for all upstream API calls
- Exponential backoff, retries, idempotency keys for inventory movements
- Serve cached asset record if upstream unavailable; mark stale and alert

### ADR-005: Security & Accessibility
- Entra ID SSO with MFA, device compliance required
- WCAG 2.1 AA compliance for mobile UI
- No OTP fallback; only managed devices

---

## 4. Data & API Contracts

### 4.1 Work Order API (OpenAPI v3.1, summary)

**Entities:**
- WorkOrder: id, status, assignedTo, assetId, SLA, criticality, serviceEntries[], evidence[], completionRecord
- Asset: id, type, location, faultCodes[], serviceHistory[]
- ServiceEntry: id, workOrderId, partId, laborTime, notes, evidence[]
- Evidence: id, workOrderId, type (photo, signature), blobUri, timestamp, immutable
- CompletionRecord: id, workOrderId, meterReading, siteContactSignature, closedBy, closedAt, immutable

**Endpoints:**
- GET /workorders?assignedTo={userId}
- POST /workorders/{id}/accept
- POST /workorders/{id}/reassign
- GET /assets/{id}
- POST /workorders/{id}/serviceentry
- POST /workorders/{id}/evidence
- POST /workorders/{id}/complete
- GET /workorders/{id}/completionRecord

**API Contract Principles:**
- All POST/PUT operations idempotent (idempotency-key header)
- Evidence uploads use SAS token, enforce immutability on closure
- CompletionRecord is read-only after closure

---

### 4.2 Integration Adapter

- RESTful connectors to asset management and inventory systems
- Managed identity authentication (OAuth 2.0 client credentials)
- 2-3 second timeout, 3 retries with exponential backoff/jitter
- Inventory movements use idempotency key per parts line

---

### 4.3 Agent Workflow API

- All agent/model calls routed via Azure API Management
- Managed identity, per-user quota, content safety policies enforced
- Sequential workflow: agent suggests, technician reviews, human approval required

---

## 5. Threat Model Considerations

- **Authentication:** Entra ID SSO, MFA, device compliance (Intune)
- **Authorization:** Role-based access (technician, planner)
- **Data Immutability:** Azure SQL and Blob Storage policies for closed orders/evidence
- **Offline Risks:** Local evidence queue encrypted at rest; sync logic handles conflicts and retries
- **API Security:** Managed identity for all upstream calls; APIM for agent/model traffic
- **Evidence Tampering:** Blob Storage immutability, completion record hash/timestamp
- **Privacy:** No PII beyond work order context; evidence stored per retention policy
- **Accessibility:** UI tested for WCAG 2.1 AA, glove/low-light usability

---

## 6. Implementable Technical Plan

### 6.1 Work Breakdown

| Phase            | Key Tasks                                                                                   | Dependencies                   |
|------------------|--------------------------------------------------------------------------------------------|--------------------------------|
| UI/UX            | Build Ionic/Angular screens (SCR-01 to SCR-04), offline store, sync queue                   | UX mockups, requirements       |
| API Layer        | Implement FastAPI endpoints, business rules, idempotency, evidence handling                 | OpenAPI contract, DB schema    |
| Integration      | Build adapters for asset management/inventory, managed identity, retry logic                 | Upstream API contracts         |
| Evidence Store   | Blob Storage setup, SAS token, immutability enforcement, offline queue                      | Azure Storage, FastAPI         |
| Agent Workflow   | Integrate Foundry agents via APIM, sequential workflow, human approval                      | Agent Framework, APIM config   |
| Security         | Entra ID SSO, device compliance, RBAC                                                      | Azure AD, Intune policies      |
| Accessibility    | WCAG 2.1 AA testing, glove/low-light usability                                              | UI testing tools               |
| CI/CD            | GitHub Actions pipeline, build provenance, environment protection                           | GitHub repo, Azure resources   |

### 6.2 Key Implementation Risks

- Offline evidence sync reliability
- Immutability enforcement on closure
- Upstream integration latency/failure
- Accessibility compliance
- Agent workflow error handling

---

## 7. Reviewable Proposal Summary

- **Architecture:** Mobile client (Ionic/Angular), FastAPI backend, Azure SQL, Blob Storage, integration adapters, agent workflow via APIM
- **Security:** Entra ID SSO, device compliance, managed identity, RBAC, evidence immutability
- **Data/API Contracts:** OpenAPI v3.1, idempotency, immutable completion records, evidence uploads
- **Threat Model:** Authentication, authorization, offline risks, evidence tampering, accessibility
- **Technical Plan:** Phased implementation, clear component boundaries, integration dependencies, CI/CD pipeline

---

**Next Steps:**  
- Review and approve architecture recommendations, ADRs, API contracts, and threat model  
- Confirm component ownership and integration boundaries  
- Validate technical plan and risk mitigation strategies  
- Proceed to implementation planning upon approval

---

**References:**  
- [Requirements Summary](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/requirements-analysis.md)
- [Technical Requirements](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/technical-requirements/Field-Service-Work-Orders-Technical-Requirements.docx)
- [UX Mockups](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/ux-mockups/Field-Service-Work-Orders-UX-Mockups.docx)

---

**This proposal is ready for review and approval.**