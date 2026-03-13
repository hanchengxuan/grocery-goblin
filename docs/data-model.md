# Grocery Goblin — Data Model Draft

## Core tables
### stores
- id
- code (`woolworths`, `coles`, `aldi`)
- name
- loyalty_program

### products
- id
- canonical_name
- brand
- size_label
- category

### product_offers
- id
- product_id
- store_id
- source_product_ref
- current_price
- unit_price_value
- unit_price_unit
- promo_flag
- promo_text
- last_seen_at

### price_snapshots
- id
- product_offer_id
- observed_price
- observed_at

### users
- id
- email
- display_name
- created_at

### loyalty_accounts
- id
- user_id
- provider (`woolworths_rewards`, `flybuys`)
- external_ref
- last_synced_at

### loyalty_tasks
- id
- loyalty_account_id
- title
- description
- target_spend
- reward_points
- start_at
- end_at
- status

## Derived logic
- basket compare joins user basket items against current offers
- loyalty ROI estimates cents-per-point and required extra spend
- future worker jobs normalize units so price comparison is meaningful
