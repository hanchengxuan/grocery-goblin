from fastapi import Depends, FastAPI
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .catalog import search_products as search_products_from_db
from .config import get_settings
from .db import get_db
from .models import Store
from .schemas import BasketRequest, BasketResponse, BasketStoreTotal, ProductSearchResult, StoreSummary

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("select 1"))
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version, "env": settings.app_env}


@app.get("/stores", response_model=list[StoreSummary])
def list_stores(db: Session = Depends(get_db)) -> list[StoreSummary]:
    rows = db.scalars(select(Store).order_by(Store.name.asc())).all()
    return [StoreSummary(code=row.code, name=row.name, loyalty_program=row.loyalty_program) for row in rows]


@app.get("/products/search", response_model=list[ProductSearchResult])
def search_products(q: str = "", db: Session = Depends(get_db)) -> list[ProductSearchResult]:
    return search_products_from_db(db, q)


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
