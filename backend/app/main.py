from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .schemas import BasketRequest, BasketResponse, BasketStoreTotal, ProductSearchResult, StoreSummary

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

STORES = [
    StoreSummary(code="woolworths", name="Woolworths", loyalty_program="Woolworths Rewards"),
    StoreSummary(code="coles", name="Coles", loyalty_program="Flybuys"),
    StoreSummary(code="aldi", name="ALDI", loyalty_program=None),
]

DEMO_PRODUCTS = [
    ProductSearchResult(product_id="ww-001", name="Bananas", store="Woolworths", price=3.90, unit_price="$3.90/kg", promo=False),
    ProductSearchResult(product_id="co-001", name="Bananas", store="Coles", price=3.70, unit_price="$3.70/kg", promo=False),
    ProductSearchResult(product_id="al-001", name="Bananas", store="ALDI", price=3.49, unit_price="$3.49/kg", promo=False),
]


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("select 1"))
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version, "env": settings.app_env}


@app.get("/stores", response_model=list[StoreSummary])
def list_stores() -> list[StoreSummary]:
    return STORES


@app.get("/products/search", response_model=list[ProductSearchResult])
def search_products(q: str = "") -> list[ProductSearchResult]:
    query = q.strip().lower()
    if not query:
        return DEMO_PRODUCTS
    return [p for p in DEMO_PRODUCTS if query in p.name.lower()]


@app.post("/basket/compare", response_model=BasketResponse)
def compare_basket(payload: BasketRequest) -> BasketResponse:
    item_count = sum(item.quantity for item in payload.items) or 1
    totals = [
        BasketStoreTotal(store="ALDI", total=round(3.49 * item_count, 2), matched_items=len(payload.items)),
        BasketStoreTotal(store="Coles", total=round(3.70 * item_count, 2), matched_items=len(payload.items)),
        BasketStoreTotal(store="Woolworths", total=round(3.90 * item_count, 2), matched_items=len(payload.items)),
    ]
    return BasketResponse(
        totals=totals,
        recommendation="Demo recommendation: ALDI is currently the cheapest fully matched basket in this stub.",
    )
