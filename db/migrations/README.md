# Database Migrations

This directory is reserved for **future schema changes** after the initial deployment.

## Initial Schema

The initial database schema is at **`db/schema.sql`** (parent directory).

Run it once to set up the database:

```bash
psql $DATABASE_URL -f db/schema.sql
```

## Future Migrations

When you need to modify the schema after deployment, create numbered migration files here:

```bash
db/migrations/
  001_add_user_preferences.sql
  002_add_alerts_table.sql
  003_add_performance_index.sql
```

### Migration File Format

```sql
-- Migration: Brief description
-- Date: YYYY-MM-DD
-- Applied after: <previous migration or "initial schema">

-- Your changes here
ALTER TABLE signals ADD COLUMN ...;
CREATE INDEX ...;

-- Rollback (optional)
-- DROP INDEX ...;
-- ALTER TABLE signals DROP COLUMN ...;
```

### Best Practices

1. **Never edit db/schema.sql** after it's been run in production
2. **Always create new migration files** for schema changes
3. **Test migrations** on a local database first
4. **Document rollback steps** when possible
5. **Keep migrations small** and focused on one change

### Running Migrations

```bash
# Run a specific migration
psql $DATABASE_URL -f db/migrations/001_add_user_preferences.sql

# Or create a migration runner script
python scripts/run_migrations.py
```

## Current Status

- ✅ Initial schema: `db/schema.sql` (includes all MVP tables)
- 📁 Migrations directory: Empty (ready for future changes)
