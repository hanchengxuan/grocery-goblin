from pydantic import BaseModel, Field


class StoreSummary(BaseModel):
    code: str
    name: str
    loyalty_program: str | None = None


class ProductSearchResult(BaseModel):
    product_id: str
    name: str
    store: str
    price: float = Field(..., ge=0)
    unit_price: str
    promo: bool = False


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
