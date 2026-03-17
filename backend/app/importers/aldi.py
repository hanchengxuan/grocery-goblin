from app.importers.base import SupermarketImportSource
from app.schemas import ProductImportRecord


class AldiImportSource(SupermarketImportSource):
    store_code = "aldi"

    def __init__(self):
        super().__init__(source_name="aldi")

    def normalize_item(self, item: dict) -> ProductImportRecord:
        return self._wrap_single_offer(
            item,
            canonical_name=item.get("name") or item.get("title") or "Unknown ALDI Product",
            brand=item.get("brand"),
            size_label=item.get("size") or item.get("package_size"),
            category=item.get("category"),
            image_url=item.get("image_url") or item.get("image"),
            barcode=item.get("barcode"),
            source_product_ref=item.get("product_id") or item.get("sku"),
            current_price=item.get("price") or item.get("current_price"),
            unit_price_value=item.get("unit_price_value"),
            unit_price_unit=item.get("unit_price_unit"),
            promo_flag=bool(item.get("promo_flag") or item.get("on_special")),
            promo_text=item.get("promo_text") or item.get("special_text"),
        )
