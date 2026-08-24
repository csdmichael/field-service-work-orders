# Field Service Work Orders — Database

PostgreSQL. Forward-only migrations in `migrations/`, numbered and never edited once merged.
`schema.sql` is the consolidated current state, regenerated after each migration.

`0002_seed.sql` holds the same rows the API seeds itself with, so the UI shows data before the
database is wired up.
