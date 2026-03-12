# Grocery Goblin — MVP PRD

## Product
Grocery Goblin is an Australian supermarket savings assistant that compares prices across Woolworths, Coles, and ALDI, and helps users optimize Woolworths Rewards and Flybuys points tasks.

## Target user
- Budget-conscious Australian households
- Students and young professionals
- Families who do weekly grocery planning
- Points/rewards optimizers

## User problems
1. I don't know which store is cheapest for my basket.
2. I don't know whether a points task is worth it.
3. I don't know how much extra spend is needed to complete a task.
4. I waste time switching between Coles, Woolworths, and ALDI.

## MVP goals
- Product search across supported stores
- Basket comparison across stores
- Rewards/Flybuys task visibility
- Task ROI analysis
- Recommended shopping strategy

## MVP features
### 1. Product search
- Search by keyword
- Return price, size, unit price, store, promotion flag

### 2. Basket optimizer
- Input shopping list
- Compare cost by store
- Suggest split basket when cheaper

### 3. Rewards/Flybuys account connection
- User connects Woolworths Rewards or Flybuys account
- Read-only task + points sync first

### 4. Task analysis
- Show current tasks
- Estimate additional spend required
- Estimate effective value of points earned
- Flag good / neutral / bad tasks

### 5. Dashboard
- Cheapest basket today
- Tasks worth doing this week
- Store-by-store savings summary

## Non-goals for MVP
- Automatic task activation
- Automatic checkout/cart filling
- Full mobile app
- Full supermarket catalog sync

## Revenue ideas
- Free tier: limited searches + one basket
- Pro: unlimited basket optimization + task analysis + alerts
- Household tier: shared lists and savings tracking

## First build order
1. Data model
2. Product/store ingestion
3. Search API
4. Basket comparison API
5. Rewards/Flybuys task ingestion
6. ROI engine
7. Minimal web dashboard
