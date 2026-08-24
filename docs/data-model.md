# Data model — Field Service Work Orders

## `work_item`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `BIGSERIAL` | Primary key |
| `title` | `TEXT` | Required |
| `location` | `TEXT` | Site the work happens at |
| `status` | `TEXT` | `new`, `in-progress`, `complete`; defaults to `new` |
| `priority` | `TEXT` | `low`, `normal`, `high`; defaults to `normal` |
| `created_at` / `updated_at` | `TIMESTAMPTZ` | Audit timestamps |

`migrations/0002_seed.sql` loads reference rows so a new environment is never empty.
