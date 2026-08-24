# Delivery plan — Field Service Work Orders

Sprints are two weeks. Each sprint closes with a demo and an approval gate.

| Sprint | Focus | Exit criteria |
| --- | --- | --- |
| Sprint 1 | Foundation: repo, pipelines, schema | CI green, API deployed |
| Sprint 2 | Core scope | Approved user stories delivered |
| Sprint 3 | Hardening and release | Tests pass, release gate approved |

## Approved scope

- Technician Mobile App (iOS/Android, managed devices)
- Integration Layer (API gateway, connects to asset/parts master)
- Upstream Systems (Asset Management, Inventory)
- Authentication (Entra ID SSO, MFA)
- Audit Record Storage (Immutable, timestamped records)
- Offline Sync Engine
- **Features:**
- List of assigned work orders, sorted by SLA risk and asset criticality
- Real-time updates (within 30 seconds)
- Accept/reassign work order (with mandatory reason for reassign)
- **UX Mockup Reference:**
- [SCR-01 Mockup](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/ux-mockups/Field-Service-Work-Orders-UX-Mockups.docx)
