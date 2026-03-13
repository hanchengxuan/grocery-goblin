from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .catalog import (
    compare_basket as compare_basket_from_db,
    search_products_by_barcode,
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
from .vision import (
    decode_barcode_from_image,
    derive_barcode_hint,
    derive_ocr_text,
    derive_query_hints,
    save_uploaded_image,
)

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

    decoded_barcode, decode_error = decode_barcode_from_image(saved)
    filename_barcode = derive_barcode_hint(file.filename or saved.name)
    barcode = decoded_barcode or filename_barcode
    barcode_status = None
    if decoded_barcode:
        barcode_status = 'decoded_from_image'
    elif filename_barcode:
        barcode_status = 'derived_from_filename'
    elif decode_error:
        barcode_status = f'barcode_decoder_unavailable: {decode_error}'
    else:
        barcode_status = 'no_barcode_detected'

    ocr_text = derive_ocr_text(file.filename or saved.name)
    hints = derive_query_hints(file.filename or saved.name)

    matches: list[GroupedProductSearchResult] = []
    if barcode:
        matches = search_products_by_barcode(db, barcode)

    if not matches:
        for hint in hints:
            results = search_products_grouped_from_db(db, hint)
            if results:
                matches = results
                break

    return VisionIdentifyResponse(
        uploaded_path=str(saved),
        barcode=barcode,
        barcode_status=barcode_status,
        ocr_text=ocr_text,
        query_hints=hints,
        matches=matches,
    )
