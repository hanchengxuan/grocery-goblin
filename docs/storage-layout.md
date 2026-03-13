# Grocery Goblin — Storage Layout

## In repo / workspace
- `projects/grocery-goblin/backend` — API and DB code
- `projects/grocery-goblin/frontend` — app/client code
- `projects/grocery-goblin/docs` — product and architecture docs

## On `/data`
Use `/data` for heavier operational artifacts.

### Recommended layout
```text
/data/grocery-goblin/
├── raw/
│   ├── woolworths/
│   ├── coles/
│   ├── aldi/
│   └── loyalty/
├── exports/
├── logs/
└── cache/
```

## Rules
- Raw HTML/JSON responses: `/data/grocery-goblin/raw/...`
- Temporary parsing/debug files: `/data/grocery-goblin/logs/...`
- Large caches: `/data/grocery-goblin/cache/...`
- Do not commit generated raw artifacts to git.
