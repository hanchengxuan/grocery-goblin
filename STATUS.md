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

## Current backend progress
- FastAPI backend scaffold exists
- Supabase database is connected via pooler
- Initial schema migration has been applied
- Reference stores have been seeded
- Retention strategy is now defined: current-offer table + raw snapshots + daily aggregates
- `/stores` reads from the real database

## Current backend progress
- `/products/search` now reads from real database rows
- Product + offer upsert path exists
- Snapshot writes happen on import path using dedupe logic
- Sample product importer has been validated against Supabase
- Retention cleanup script exists for snapshot rollup/purge

## Current backend progress
- Real basket comparison now runs from stored `product_offers`
- Basket recommendation prefers fuller basket coverage, then lower price
- Default `/products/search` now returns grouped product matches with per-store pricing
- `/products/search-flat` remains available for raw per-offer debugging
- `/vision/identify-product` now supports barcode-first, OCR, and vision-provider pipeline stages
- Products can store canonical barcode values for future scan-based lookup
- Real barcode decoder path is integrated and enabled via `libzbar`
- OCR extraction code path is integrated and ready when `tesseract` is available
- Vision provider interface + placeholder identifier are integrated for future multimodal model hookup
- Sample data validates end-to-end grouped search + compare flow

## Current backend progress
- Importer scaffolding exists with a generic JSON file import path
- ALDI now has a real searchable product API path wired into the importer layer
- Vision identification can now feed into structured product matching
- Gemini is the main free vision provider and returns stable structured product fields on tested grocery photos

## Next build target
1. Add supermarket-specific importer interfaces for Woolworths / Coles / ALDI
2. Expand product search filtering/sorting (category, promo, store)
3. Add scheduled jobs for import + retention
4. Add lightweight API auth / admin protection for import endpoints/scripts
5. Improve OCR text cleaning and ranking fusion
