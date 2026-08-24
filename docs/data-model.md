# Data model — Field Service Work Orders

## `work_item`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `BIGSERIAL` | Primary key |
| `title` | `TEXT` | Required |
| `status` | `TEXT` | Defaults to `new` |
| `created_at` / `updated_at` | `TIMESTAMPTZ` | Audit timestamps |
