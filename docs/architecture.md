# Grocery Goblin — Architecture

## MVP architecture
- **Client:** React Native + Expo
- **API:** FastAPI on Oracle instance
- **Database:** PostgreSQL
- **Background jobs:** Python workers / cron on Oracle instance
- **Optional managed services:** Supabase for auth/storage/row-level access patterns

## Why this shape
- Cheap to run on existing Oracle infrastructure
- Easy to keep scraping/automation on the same host as scheduled jobs
- Clean separation between user-facing API and data ingestion jobs
- Leaves room to later split out a worker repo only if it becomes operationally necessary

## Suggested services
1. `api`
   - search endpoints
   - basket pricing endpoint
   - loyalty task endpoints
2. `worker`
   - supermarket price ingestion
   - loyalty task sync
   - snapshotting / normalization
3. `db`
   - products
   - price snapshots
   - users
   - loyalty accounts/tasks
