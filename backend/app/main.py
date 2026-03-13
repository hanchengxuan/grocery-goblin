from fastapi import Depends, FastAPI
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .catalog import compare_basket as compare_basket_from_db, search_products as search_products_from_db
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
def compare_basket(payload: BasketRequest, db: Session = Depends(get_db)) -> BasketResponse:
    return compare_basket_from_db(db, payload.items)
