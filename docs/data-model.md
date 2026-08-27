# Data model — Field service Work Orders

## `work_order`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `BIGSERIAL` | Primary key |
| `title` | `TEXT` | Required |
| `reference` | `TEXT` | Optional |
| `status` | `TEXT` | `new`, `in-progress`, `complete`; defaults to `new` |
| `priority` | `TEXT` | `low`, `normal`, `high`; defaults to `normal` |
| `created_at` / `updated_at` | `TIMESTAMPTZ` | Audit timestamps |

`migrations/0002_seed.sql` loads placeholder rows so a new environment is never empty.
