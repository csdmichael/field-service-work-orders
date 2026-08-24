# Delivery plan — Field Service Work Orders

Sprints are two weeks. Each sprint closes with a demo and an approval gate.

| Sprint | Focus | Exit criteria |
| --- | --- | --- |
| Sprint 1 | Foundation: repo, pipelines, schema | CI green, API deployed |
| Sprint 2 | Core scope | Approved user stories delivered |
| Sprint 3 | Hardening and release | Tests pass, release gate approved |

## Approved scope

- [Field Service Work Orders - Requirements.docx](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/requirements/Field-Service-Work-Orders-Requirements.docx)
- Defines scope, epics, features, user stories, acceptance criteria, non-functional requirements, traceability, assumptions, and out-of-scope items.
- **Purpose & Scope:** Technician mobile app for field service work orders; demo artifact for traceability and document management.
- **Epic:** Receive, diagnose, and complete work orders from a handheld device.
- **Features & User Stories:**
- FEAT-01: Work Order Queue and Dispatch (US-101, US-102)
- FEAT-02: Asset Detail and Diagnostics (US-201, US-202)
- FEAT-03: Service Log and Parts (US-301, US-302)
- FEAT-04: Completion and Sign-off (US-401, US-402)
- **Non-Functional Requirements:** Performance, availability, offline capability, security, accessibility, auditability, integration.
- **Traceability:** Features mapped to screens in UX mockups.
- **Assumptions & Out of Scope:** Upstream systems, device management, network coverage, excluded features.
