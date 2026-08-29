**Field Service Work Orders – Plan Stage Requirements Proposal**

---

### 1. Epic

**EPIC-01: Field Service Work Orders**
> As a maintenance operations team, we want technicians to receive, diagnose, and complete work orders from a handheld device, so that asset downtime falls and every intervention leaves a complete, auditable record.

---

### 2. Features & User Stories

#### FEAT-01: Work Order Queue and Dispatch
**Description:** Live, prioritized list of open work orders ranked by SLA risk and asset criticality; technician can accept/reassign orders.

- **US-101:** See assigned work orders ranked by SLA risk and asset criticality.
  - **Acceptance Criteria:**
    - Queue loads with open work orders sorted by SLA risk, then asset criticality.
    - New dispatches appear within 30 seconds, no manual refresh required.
  - **Tasks:**
    - Implement queue rendering logic.
    - Integrate real-time update mechanism.
    - UX: SCR-01 mockup alignment.
  - **Dependencies:** Asset management system integration; real-time sync.
  - **Risks:** Delayed updates due to network issues.

- **US-102:** Accept or reassign a work order.
  - **Acceptance Criteria:**
    - Accepting an order updates status to In Progress; planner sees change.
    - Reassigning requires mandatory reason, recorded against order.
  - **Tasks:**
    - Implement accept/reassign actions.
    - Record reason for reassignment.
    - UX: SCR-01 mockup alignment.
  - **Dependencies:** Work order API; planner interface.
  - **Risks:** Data consistency on reassignment.

---

#### FEAT-02: Asset Detail and Diagnostics
**Description:** Asset identity, fault codes, guided troubleshooting, and service history in one place.

- **US-201:** View asset’s active fault codes and recent service events.
  - **Acceptance Criteria:**
    - Asset ID, type, location, and active fault codes shown.
    - Ten most recent service events listed, newest first.
  - **Tasks:**
    - Fetch and display asset/fault/service data.
    - UX: SCR-02 mockup alignment.
  - **Dependencies:** Asset management system; service history API.
  - **Risks:** Incomplete data from upstream.

- **US-202:** Guided troubleshooting steps for reported fault.
  - **Acceptance Criteria:**
    - Matching troubleshooting steps shown in order for known fault codes.
    - If no match, escalation to senior engineer offered; gap recorded.
  - **Tasks:**
    - Integrate diagnostics agent workflow.
    - Implement escalation and gap recording.
    - UX: SCR-02 mockup alignment.
  - **Dependencies:** Microsoft Foundry agent; APIM gateway.
  - **Risks:** Agent workflow failure; escalation delays.

---

#### FEAT-03: Service Log and Parts
**Description:** Log labor time, parts used, photos, and notes; inventory decremented at point of use.

- **US-301:** Log labor time and parts used.
  - **Acceptance Criteria:**
    - On saving, stock decremented once per part.
    - Out-of-stock blocks entry; substitute/back-order offered.
  - **Tasks:**
    - Implement labor/parts logging.
    - Integrate inventory API.
    - UX: SCR-03 mockup alignment.
  - **Dependencies:** Inventory system; offline store.
  - **Risks:** Inventory sync errors; offline capture reliability.

- **US-302:** Attach photos and notes to work order.
  - **Acceptance Criteria:**
    - Photos attached offline are queued and uploaded on reconnect.
    - Attachments/notes become read-only after closure.
  - **Tasks:**
    - Implement photo/note attachment and offline queue.
    - Enforce read-only state post-closure.
    - UX: SCR-03 mockup alignment.
  - **Dependencies:** Azure Blob Storage; offline sync.
  - **Risks:** Evidence loss on sync failure.

---

#### FEAT-04: Completion and Sign-off
**Description:** Verified meter readings, dual signature, tamper-evident completion record.

- **US-401:** Capture site-contact sign-off with verified meter readings.
  - **Acceptance Criteria:**
    - Closure requires site-contact signature and meter reading.
    - Out-of-tolerance reading blocks closure; discrepancy raised.
  - **Tasks:**
    - Implement signature capture and meter reading validation.
    - Discrepancy handling.
    - UX: SCR-04 mockup alignment.
  - **Dependencies:** Blob storage for signatures; validation logic.
  - **Risks:** Signature capture reliability; closure blocking logic.

- **US-402:** Tamper-evident record for audit.
  - **Acceptance Criteria:**
    - Closed order produces timestamped, immutable record with all relevant data.
    - Records retained per asset retention policy.
  - **Tasks:**
    - Implement immutable record creation.
    - Enforce retention policy.
    - UX: SCR-04 mockup alignment.
  - **Dependencies:** Azure SQL; Blob Storage immutability.
  - **Risks:** Data immutability enforcement.

---

### 3. Non-Functional Requirements (NFRs)

| Category      | Requirement                                                        | Target                | Tasks / Risks                      |
|---------------|--------------------------------------------------------------------|-----------------------|------------------------------------|
| Performance   | Work queue and asset detail render over site network               | <2 seconds            | Optimize API and UI; network risk  |
| Availability  | Service platform uptime during shift hours                        | 99.9%                 | Azure App Service config           |
| Offline       | View accepted order and log work with no connectivity              | Full offline capture  | Durable offline store; sync risk   |
| Security      | Authentication and device trust                                   | Entra ID SSO + MFA    | Device compliance; auth risk       |
| Accessibility | Mobile interface usable with gloves and in low light               | WCAG 2.1 AA           | UI testing; accessibility risk     |

---

### 4. Dependencies

- **Asset Management System:** Source of work orders, asset data, service history.
- **Inventory System:** Parts stock, movement API.
- **Microsoft Foundry Agent Framework:** Diagnostics and troubleshooting agent.
- **Azure API Management:** Model traffic routing, authentication, quotas.
- **Azure SQL Database:** Work order, service entry, completion record storage.
- **Azure Blob Storage:** Evidence (photos, signatures), immutability.
- **Intune/Entra ID:** Device compliance and authentication.

---

### 5. Risks

- **Network Reliability:** Site wireless coverage is intermittent; offline store and sync must be robust.
- **Data Consistency:** Real-time updates, inventory decrements, and reassignment actions must be idempotent.
- **Evidence Integrity:** Photos/signatures must be retained and immutable post-closure.
- **Agent Workflow:** Diagnostics agent must never bypass human approval; escalation must be reliable.
- **Accessibility:** UI must be usable in harsh environments (gloves, low light).

---

### 6. Traceability

- **Epic → Feature → User Story:** All user stories are mapped to features and the epic, with acceptance criteria traceable to Azure DevOps work items.
- **UX Alignment:** Each feature maps to a specific screen (SCR-01 to SCR-04) per UX mockups.
- **NFRs:** Tracked as separate work items, not embedded in story acceptance criteria.

---

### 7. Proposal Summary

This proposal decomposes the approved requirements and UX inputs into traceable epics, features, user stories, tasks, acceptance criteria, dependencies, and risks. All user stories are ready for Azure DevOps import, with acceptance criteria included. Non-functional requirements are tracked separately. No external system changes are claimed; all integrations and workflow steps require human approval and verified tool output.

**Next Steps:** Review and approve this proposal. Upon approval, work items will be generated and mapped to Azure DevOps, with traceability to intake documents and UX mockups.

---

**Attachments:**  
- [Requirements Intake Document](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/requirements/Field-Service-Work-Orders-Requirements.docx)  
- [Technical Requirements](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/technical-requirements/Field-Service-Work-Orders-Technical-Requirements.docx)  
- [UX Mockups](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/ux-mockups/Field-Service-Work-Orders-UX-Mockups.docx)

---

**Please review and provide approval or feedback.**