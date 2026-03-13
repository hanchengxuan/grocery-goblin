# Grocery Goblin — Status

## Summary
Grocery Goblin is an Australian grocery savings assistant focused on basket price comparison and loyalty-task ROI.

## Decisions from channel discussion (2026-03-12)
- **Name:** Grocery Goblin
- **Primary goal:** Compare grocery baskets across Woolworths / Coles / ALDI and help optimize Woolworths Rewards + Flybuys tasks
- **Recommended architecture:** Start with **one monorepo**
- **Tech direction:**
  - Frontend/mobile: React Native + Expo
  - API: FastAPI
  - Database: PostgreSQL
  - Optional managed backend: Supabase for auth/data APIs
  - Automation/scraping/cron: Oracle instance
- **Early product posture:**
  - Start read-only
  - Price comparison first
  - Task ROI analysis before any task activation
- **Repo recommendation:** `grocery-goblin`
- **GitHub note:** repo creation was previously blocked by missing `createRepository` token permission, but the repo now exists at `https://github.com/hanchengxuan/grocery-goblin.git`

## Current state
- Initial docs/scaffold existed:
  - `README.md`
  - `PRD.md`
  - `TASKS.md`
  - `NAME.md`
- Workspace commit previously recorded: `3a1d8ca` — `Start Grocery Goblin project scaffold`
- This pass begins turning the docs-only scaffold into a runnable starter monorepo.

## Next build target
1. Create runnable FastAPI backend skeleton
2. Add shared docs for repo structure and API/data model direction
3. Add environment examples and dev commands
4. Prepare the project to sync/push to the GitHub repo
