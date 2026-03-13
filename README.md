# Grocery Goblin

Australian grocery savings assistant for basket comparison and loyalty-task ROI.

## Stack
- **Mobile/UI direction:** React Native + Expo
- **API:** FastAPI
- **Database:** PostgreSQL
- **Automation workers:** Oracle instance
- **Optional backend services:** Supabase for auth/storage/data APIs

## Product goals
- Compare grocery products and baskets across Woolworths / Coles / ALDI
- Surface Woolworths Rewards and Flybuys tasks
- Estimate task ROI and extra spend required
- Recommend the cheapest practical shopping strategy

## Monorepo layout
```text
projects/grocery-goblin/
├── backend/          # FastAPI app
├── frontend/         # Expo app scaffold
├── docs/             # architecture, schema, notes
├── README.md
├── PRD.md
├── STATUS.md
└── TASKS.md
```

## Quick start
### Backend
```bash
cd projects/grocery-goblin/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open: <http://127.0.0.1:8000/health>

## Current implementation slice
- FastAPI health endpoint
- Supabase-backed stores table
- Product + offer import/upsert path
- Real `/products/search` backed by DB rows
- Snapshot history write path with retention scaffolding
- Basket pricing endpoint still stubbed, next to be connected to real offer data

## Notes
- Start read-only for supermarket and loyalty integrations
- Price comparison first, automation later
- Keep the MVP as one repo until deployment/lifecycle pressure justifies a split
