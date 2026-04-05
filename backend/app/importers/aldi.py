from pathlib import Path
import json
import requests

from app.importers.base import SupermarketImportSource
from app.schemas import ProductImportRecord


class AldiImportSource(SupermarketImportSource):
    store_code = "aldi"
    api_base = "https://api.aldi.com.au"

    def __init__(self):
        super().__init__(source_name="aldi")

    def fetch_category_tree(self, *, service_point: str = "G452") -> dict:
        response = requests.get(
            f"{self.api_base}/v2/product-category-tree",
            params={"serviceType": "walk-in", "servicePoint": service_point},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def fetch_search_results(self, query: str, *, service_point: str = "G452", limit: int = 12, offset: int = 0) -> dict:
        params = {
            "currency": "AUD",
            "serviceType": "walk-in",
            "limit": limit,
            "offset": offset,
            "sort": "relevance",
            "servicePoint": service_point,
            "query": query,
        }
        response = requests.get(
            f"{self.api_base}/v3/product-search",
            params=params,
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def load(self, path: Path) -> list[ProductImportRecord]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            raw_items = payload.get("data", payload.get("products", payload.get("items", [])))
        else:
            raw_items = payload
        return [self.normalize_item(item) for item in raw_items]

    def normalize_item(self, item: dict) -> ProductImportRecord:
        price = item.get("price") or {}
        categories = item.get("categories") or []
        category = categories[-1].get("name") if categories else None
        asset = next((a for a in (item.get("assets") or []) if a.get("assetType", "").startswith("FR")), None)
        image_url = None
        if asset and asset.get("url"):
            image_url = asset["url"].replace("{width}", "800").replace("{slug}", item.get("urlSlugText") or item.get("sku") or "product")
        return self._wrap_single_offer(
            item,
            canonical_name=item.get("name") or "Unknown ALDI Product",
            brand=item.get("brandName"),
            size_label=item.get("sellingSize"),
            category=category.lower() if isinstance(category, str) else category,
            image_url=image_url,
            barcode=None,
            source_product_ref=item.get("sku"),
            current_price=(price.get("amount") or 0) / 100,
            unit_price_value=(price.get("comparison") / 100) if price.get("comparison") is not None else None,
            unit_price_unit=(price.get("comparisonDisplay") or "").split(" per ")[-1] if price.get("comparisonDisplay") and " per " in price.get("comparisonDisplay") else None,
            promo_flag=bool(price.get("wasPriceDisplay") or price.get("savingsDisplay")),
            promo_text=price.get("savingsDisplay") or price.get("additionalInfo"),
        )
