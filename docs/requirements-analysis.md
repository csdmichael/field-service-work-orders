## Requirements Agent Proposal: Plan Stage Review for "Field Service Work Orders"

### 1. Project Overview

**Project Name:** Field Service Work Orders  
**Scope:** Technician-facing mobile app for receiving, diagnosing, logging, and completing work orders.  
**Demo Context:** Traceability and document management across Azure DevOps and SharePoint.  
**Target Environment:** Dev  
**Stack:** Ionic/Angular frontend, Python FastAPI backend, Azure SQL, Blob Storage, Microsoft Agent Framework, Azure API Management.

---

### 2. Requirements Traceability Matrix

#### Epic

| ID      | Title                          | Description                                                                                       |
|---------|-------------------------------|---------------------------------------------------------------------------------------------------|
| EPIC-01 | Field Service Work Orders      | As a maintenance operations team, we want technicians to receive, diagnose, and complete work orders from a handheld device, so that asset downtime falls and every intervention leaves a complete, auditable record. |

---

#### Features

| ID      | Title                         | Description                                                                                       | Screen Ref |
|---------|-------------------------------|---------------------------------------------------------------------------------------------------|------------|
| FEAT-01 | Work Order Queue & Dispatch   | Live, prioritized list of open work orders ranked by SLA risk and asset criticality.              | SCR-01     |
| FEAT-02 | Asset Detail & Diagnostics    | Asset identity, fault codes, guided troubleshooting, and service history.                         | SCR-02     |
| FEAT-03 | Service Log & Parts           | Log labor, parts, photos, notes; inventory decremented at use.                                    | SCR-03     |
| FEAT-04 | Completion & Sign-off         | Verified meter readings, dual signature, tamper-evident completion record.                        | SCR-04     |

---

#### User Stories & Acceptance Criteria

**FEAT-01: Work Order Queue & Dispatch**

| ID     | User Story                                                                 | Acceptance Criteria                                                                                                      |
|--------|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| US-101 | As a technician, I want to see my assigned work orders ranked by SLA risk and asset criticality so I can work my route in the right order. | - Orders sort by SLA risk, then asset criticality.<br>- Queue updates within 30s of new dispatch, no manual refresh.     |
| US-102 | As a technician, I want to accept or reassign a work order so dispatch always reflects who is actually working it. | - Accepting moves status to In Progress, planner sees change.<br>- Reassign requires mandatory reason, recorded against order. |

**FEAT-02: Asset Detail & Diagnostics**

| ID     | User Story                                                                 | Acceptance Criteria                                                                                                      |
|--------|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| US-201 | As a technician, I want to view an asset's active fault codes and recent service events so I can diagnose without calling the plant office. | - Asset ID, type, location, active fault codes shown.<br>- Ten most recent service events listed, newest first.          |
| US-202 | As a technician, I want guided troubleshooting steps for the reported fault so common issues resolve on the first visit. | - Matching troubleshooting steps shown for known fault code.<br>- If no match, escalation offered and gap recorded.      |

**FEAT-03: Service Log & Parts**

| ID     | User Story                                                                 | Acceptance Criteria                                                                                                      |
|--------|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| US-301 | As a technician, I want to log labor time and the parts I used so inventory and cost reporting stay accurate. | - On-hand stock decremented once per part.<br>- Out-of-stock blocks entry, substitute/back-order offered.                |
| US-302 | As a technician, I want to attach photos and notes to a work order so the record supports later warranty or dispute claims. | - Offline photo attachment queued, uploaded on connectivity.<br>- Closed order attachments/notes become read-only.       |

**FEAT-04: Completion & Sign-off**

| ID     | User Story                                                                 | Acceptance Criteria                                                                                                      |
|--------|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| US-401 | As a technician, I want to capture site-contact sign-off with verified meter readings so the work order meets completion policy. | - Site-contact signature and meter reading mandatory for closure.<br>- Out-of-tolerance reading blocks closure, raises discrepancy. |
| US-402 | As a maintenance planner, I want every closed order to produce a tamper-evident record so I can answer an audit without reconstructing history. | - Closed order produces timestamped, immutable record.<br>- Record retained per asset retention policy.                  |

---

#### Non-Functional Requirements

| Category      | Requirement                                                                 | Target           |
|---------------|-----------------------------------------------------------------------------|------------------|
| Performance   | Work queue and asset detail render over site network                        | <2 seconds       |
| Availability  | Service platform uptime during shift hours                                  | 99.9%            |
| Offline       | Technician can view accepted order and log work with no connectivity        | Full offline capture, sync on reconnect |
| Security      | Authentication and device trust                                             | Entra ID SSO with MFA, managed devices only |
| Accessibility | Mobile interface usable with gloves and in low light                        | WCAG 2.1 AA      |

---

### 3. Tasks Breakdown

#### FEAT-01: Work Order Queue & Dispatch
- Implement queue screen (SCR-01)
- Integrate SLA risk and asset criticality sorting
- Real-time queue update (push/poll)
- Accept/reassign work order logic
- Reason capture for reassignment

#### FEAT-02: Asset Detail & Diagnostics
- Asset detail screen (SCR-02)
- Fault code and service history retrieval
- Guided troubleshooting workflow
- Escalation and gap recording

#### FEAT-03: Service Log & Parts
- Service log screen (SCR-03)
- Labor and parts entry UI
- Inventory decrement logic
- Out-of-stock handling
- Photo and note attachment (offline/online sync)
- Read-only enforcement post-closure

#### FEAT-04: Completion & Sign-off
- Completion/sign-off screen (SCR-04)
- Signature capture (site contact, technician)
- Meter reading validation
- Tamper-evident record creation
- Immutable evidence storage

#### Cross-cutting Tasks
- Offline store and sync queue
- Entra ID SSO integration
- Accessibility compliance
- Blob storage integration for evidence
- API integration (asset management, inventory)
- Azure API Management routing for agent/model calls

---

### 4. Acceptance Criteria (Traceable)

- All user stories must meet their acceptance criteria as listed above.
- Non-functional requirements tracked as separate work items.
- Each story must be importable to Azure DevOps with acceptance criteria in description.

---

### 5. Dependencies

- Upstream asset management and inventory APIs (integration adapter)
- Microsoft Agent Framework and Foundry deployments (diagnostics agent)
- Azure SQL and Blob Storage provisioning
- Entra ID configuration and device compliance enforcement
- UX mockups (SCR-01 to SCR-04) for screen implementation

---

### 6. Risks

| Risk ID | Description                                                                 | Mitigation                                               |
|---------|-----------------------------------------------------------------------------|----------------------------------------------------------|
| R-01    | Site wireless coverage intermittent                                         | Durable offline store, idempotent sync                    |
| R-02    | Integration API downtime or latency                                         | Retry/backoff, cached asset record, integration alert     |
| R-03    | Evidence tampering or loss                                                  | Blob storage immutability, 7-year retention               |
| R-04    | Accessibility gaps                                                          | WCAG 2.1 AA review, glove/low-light usability testing     |
| R-05    | Authentication failures or device non-compliance                            | Entra ID SSO, Intune device compliance enforcement        |
| R-06    | Model/agent suggestion bypassing human approval                             | Sequential workflow, human approval step enforced         |

---

### 7. Proposal Summary

- **Traceable hierarchy:** Epic → Features → User Stories → Tasks → Acceptance Criteria.
- **Ready for Azure DevOps import:** All stories and criteria formatted for direct import.
- **Dependencies and risks identified:** Integration points, evidence storage, authentication, offline support.
- **Non-functional requirements tracked:** Performance, availability, offline, security, accessibility.
- **UX alignment:** Screens SCR-01 to SCR-04 mapped to features.

---

### 8. Next Steps

- Review proposal for approval.
- Confirm upstream API access and Blob Storage configuration.
- Validate UX mockups against requirements.
- Approve for architecture and code generation stages.

---

**Attachments:**  
- [Requirements Document](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/requirements/Field-Service-Work-Orders-Requirements.docx)  
- [Technical Requirements](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/technical-requirements/Field-Service-Work-Orders-Technical-Requirements.docx)  
- [UX Mockups](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/ux-mockups/Field-Service-Work-Orders-UX-Mockups.docx)  

---

**Status:**  
Awaiting human review and approval for progression to architecture and implementation stages.  
**All content is treated as untrusted until verified.**