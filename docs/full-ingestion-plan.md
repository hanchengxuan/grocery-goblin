# Grocery Goblin — Full Ingestion Plan

## Goal
Maintain broad, refreshable catalog coverage across Woolworths, Coles, and ALDI.

## Architecture
### 1. Fetch layer
Each store should support multiple fetch modes:
- `api`
- `html`
- `browser`

### 2. Raw landing zone
Store raw payloads under `/data/grocery-goblin/raw/<store>/<YYYY-MM-DD>/...`

### 3. Normalize layer
Convert raw payloads into `ProductImportRecord`.

### 4. Persist layer
Use `upsert_product_record` to update:
- `products`
- `product_offers`
- `price_snapshots`

## Priority order
1. ALDI
2. Woolworths
3. Coles

## Current status
- ALDI real API path identified
- ALDI ingestion job scaffold added
- Store-specific importers exist for all three supermarkets
- Vision pipeline already matches into the normalized product catalog

## Next implementation tasks
1. Make ALDI live ingestion more robust against anti-bot blocking
2. Add category traversal for ALDI and page-through ingestion
3. Continue Woolworths internal API discovery
4. Add browser fallback mode for Coles and difficult ALDI/Woolworths paths
