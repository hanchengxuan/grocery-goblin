from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .catalog import (
    compare_basket as compare_basket_from_db,
    search_products_flat as search_products_flat_from_db,
    search_products_grouped as search_products_grouped_from_db,
)
from .config import get_settings
from .db import get_db
from .models import Store
from .schemas import (
    BasketRequest,
    BasketResponse,
    GroupedProductSearchResult,
    ProductSearchResult,
    StoreSummary,
    VisionIdentifyResponse,
)
from .vision import save_uploaded_image
from .vision_pipeline import run_vision_pipeline

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


@app.get("/products/search", response_model=list[GroupedProductSearchResult])
def search_products(q: str = "", db: Session = Depends(get_db)) -> list[GroupedProductSearchResult]:
    return search_products_grouped_from_db(db, q)


@app.get("/products/search-flat", response_model=list[ProductSearchResult])
def search_products_flat(q: str = "", db: Session = Depends(get_db)) -> list[ProductSearchResult]:
    return search_products_flat_from_db(db, q)


@app.post("/basket/compare", response_model=BasketResponse)
def compare_basket(payload: BasketRequest, db: Session = Depends(get_db)) -> BasketResponse:
    return compare_basket_from_db(db, payload.items)


@app.post("/vision/identify-product", response_model=VisionIdentifyResponse)
async def identify_product_from_image(file: UploadFile = File(...), db: Session = Depends(get_db)) -> VisionIdentifyResponse:
    suffix = Path(file.filename or "upload.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        temp_path = Path(tmp.name)

    saved = save_uploaded_image(temp_path, file.filename)
    temp_path.unlink(missing_ok=True)
    return run_vision_pipeline(db, saved, file.filename)
