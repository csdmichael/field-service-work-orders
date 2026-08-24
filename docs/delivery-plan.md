# Delivery plan — Field Service Work Orders

Sprints are two weeks. Each sprint closes with a demo and an approval gate.

| Sprint | Focus | Exit criteria |
| --- | --- | --- |
| Sprint 1 | Foundation: repo, pipelines, schema | CI green, API deployed |
| Sprint 2 | Core scope | Approved user stories delivered |
| Sprint 3 | Hardening and release | Tests pass, release gate approved |

## Approved scope

- Technician Mobile App (iOS/Android, managed via Intune)
- Integration Layer (API Gateway, connects to asset/parts master data)
- Upstream Systems (Enterprise Asset Management, Inventory)
- Authentication (Entra ID SSO with MFA)
- Document Management (SharePoint)
- Work Item Tracking (Azure DevOps)
- Reporting (Power BI dashboards)
- "Field Service Work Orders - UX Mockups.docx" ([link](https://github.com/csdmichael/field-service-work-orders/blob/main/docs/intake/ux-mockups/Field-Service-Work-Orders-UX-Mockups.docx))
- **SCR-01:** Work Order Queue and Dispatch
- Live, prioritized list of work orders (SLA risk, asset criticality)
- Accept/reassign actions
- **SCR-02:** Asset Detail and Diagnostics
