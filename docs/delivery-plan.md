# Delivery plan — Field service Work Orders

Sprints are two weeks. Each sprint closes with a demo and an approval gate.

| Sprint | Focus | Exit criteria |
| --- | --- | --- |
| Sprint 1 | Foundation: repo, pipelines, schema | CI green, API deployed |
| Sprint 2 | Core scope | Approved user stories delivered |
| Sprint 3 | Hardening and release | Tests pass, release gate approved |

## Approved scope

- **Database migrations** under `infrastructure/db/migrations/` creating/altering tables noted above plus indexes for SLA risk + criticality sorting.
- **Configuration**: environment variables for APIM endpoint, Foundry agent IDs, Blob containers, tolerance thresholds, offline cache TTL.
- **CI updates**: GitHub Actions workflow to run backend unit tests (pytest), frontend tests (Jest + Cypress component tests), linting, and DB migration check.
- **Offline conflict handling**: implement per-record sync status + idempotent transition tokens to prevent duplicate state changes.
- **Diagnostics agent latency**: wrap agent calls with timeout + fallback messaging; ensure UI doesn’t block critical path.
- **Immutable completion enforcement**: DB transaction plus Blob legal hold to prevent edits; add monitoring for unauthorized write attempts.
- **Inventory consistency**: idempotency keys plus reconciliation job for stuck “pending” entries.
- **Attachment storage cost**: lifecycle management for drafts, immutability only on closure.
- **Traceability**: Every change references corresponding user story ID and acceptance criteria.
- **Security**: Verify Entra claim checks on every endpoint/component, no secrets committed, managed identity only.
- **Offline behavior**: Ensure caches mark stale timestamps and UI indicates pending sync.
- **Idempotency & concurrency**: Review transaction scopes, idempotency tokens, and retry logic.
