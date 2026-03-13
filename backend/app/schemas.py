from pydantic import BaseModel, Field


class StoreSummary(BaseModel):
    code: str
    name: str
    loyalty_program: str | None = None


class ProductSearchResult(BaseModel):
    product_id: str
    name: str
    brand: str | None = None
    image_url: str | None = None
    barcode: str | None = None
    store: str
    price: float = Field(..., ge=0)
    unit_price: str
    promo: bool = False
    category: str | None = None


class StorePriceResult(BaseModel):
    store_code: str
    store_name: str
    price: float = Field(..., ge=0)
    unit_price: str = ""
    promo: bool = False
    source_product_ref: str | None = None
    image_url: str | None = None


class GroupedProductSearchResult(BaseModel):
    product_id: str
    name: str
    brand: str | None = None
    size_label: str | None = None
    category: str | None = None
    image_url: str | None = None
    barcode: str | None = None
    stores: list[StorePriceResult]


class ProductImportOffer(BaseModel):
    store_code: str
    source_product_ref: str | None = None
    image_url: str | None = None
    current_price: float = Field(..., ge=0)
    unit_price_value: float | None = Field(default=None, ge=0)
    unit_price_unit: str | None = None
    promo_flag: bool = False
    promo_text: str | None = None


class ProductImportRecord(BaseModel):
    canonical_name: str
    brand: str | None = None
    size_label: str | None = None
    category: str | None = None
    image_url: str | None = None
    barcode: str | None = None
    offers: list[ProductImportOffer]


class BasketItem(BaseModel):
    query: str
    quantity: int = Field(default=1, ge=1)


class BasketRequest(BaseModel):
    items: list[BasketItem]


class BasketStoreTotal(BaseModel):
    store: str
    total: float = Field(..., ge=0)
    matched_items: int = Field(..., ge=0)


class BasketResponse(BaseModel):
    currency: str = "AUD"
    totals: list[BasketStoreTotal]
    recommendation: str


class VisionIdentifyResponse(BaseModel):
    uploaded_path: str
    barcode: str | None = None
    ocr_text: str | None = None
    query_hints: list[str]
    matches: list[GroupedProductSearchResult]
