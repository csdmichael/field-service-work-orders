-- Field Service Work Orders — consolidated schema
CREATE TABLE IF NOT EXISTS work_item (
    id           BIGSERIAL PRIMARY KEY,
    title        TEXT        NOT NULL,
    status       TEXT        NOT NULL DEFAULT 'new',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
