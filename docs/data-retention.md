# Grocery Goblin — Data Retention Policy

## Principle
- **Postgres/Supabase** stores structured product, offer, price-history, and user-facing data.
- **`/data` storage** keeps raw scrape/debug artifacts and short-lived operational files.
- Do **not** keep unlimited raw snapshots or raw HTML in the primary database.

## Database retention strategy
### `product_offers`
- One row per current product/store offer state.
- Always updated in place.
- Represents the latest known truth.

### `price_snapshots`
- Store only meaningful history points.
- Write a new snapshot when:
  - price changed, or
  - promo state changed, or
  - unit price changed, or
  - the offer has not been confirmed in the last 24 hours.

### `daily_price_aggregates`
- Long-lived compressed history.
- One row per `(product_offer_id, day)`.
- Tracks min/max/avg and observation count.

## Retention windows
### Raw `price_snapshots`
- Keep full snapshots for **30 days**.

### Daily aggregates
- Keep indefinitely for now.
- Can later be rolled into weekly/monthly summaries if needed.

### Raw scrape artifacts in `/data`
- Keep **7 to 30 days** depending on debugging needs.
- Default target path:
  - `/data/grocery-goblin/raw/<source>/<YYYY-MM-DD>/...`

## Suggested refresh cadence
### Default products
- refresh **2x/day**

### Hot/promotional products
- refresh **4x/day** later if needed

## Cleanup jobs
1. Roll up recent raw snapshots into `daily_price_aggregates`
2. Delete raw snapshots older than 30 days
3. Delete raw files in `/data/grocery-goblin/raw` older than configured TTL

## Why this works
- keeps current queries fast
- preserves useful pricing history
- prevents the database from growing uncontrollably
- keeps debugging artifacts out of the business database
