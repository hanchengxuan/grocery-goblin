from pathlib import Path
import json
from typing import Iterable

from app.schemas import ProductImportRecord


class ImportSource:
    def __init__(self, source_name: str):
        self.source_name = source_name

    def load(self, path: Path) -> list[ProductImportRecord]:
        raise NotImplementedError


class JsonFileImportSource(ImportSource):
    def __init__(self):
        super().__init__(source_name="json_file")

    def load(self, path: Path) -> list[ProductImportRecord]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            records = payload.get("products", [])
        else:
            records = payload
        return [ProductImportRecord.model_validate(item) for item in records]


class SupermarketImportSource(ImportSource):
    store_code: str | None = None

    def load(self, path: Path) -> list[ProductImportRecord]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            raw_items = payload.get("products", payload.get("items", []))
        else:
            raw_items = payload
        return [self.normalize_item(item) for item in raw_items]

    def normalize_item(self, item: dict) -> ProductImportRecord:
        raise NotImplementedError

    def _wrap_single_offer(self, item: dict, *, canonical_name: str, brand: str | None, size_label: str | None, category: str | None, image_url: str | None, barcode: str | None, source_product_ref: str | None, current_price: float | int | None, unit_price_value: float | int | None = None, unit_price_unit: str | None = None, promo_flag: bool = False, promo_text: str | None = None) -> ProductImportRecord:
        if not self.store_code:
            raise ValueError("store_code must be set on supermarket importer")
        return ProductImportRecord.model_validate(
            {
                "canonical_name": canonical_name,
                "brand": brand,
                "size_label": size_label,
                "category": category,
                "image_url": image_url,
                "barcode": barcode,
                "offers": [
                    {
                        "store_code": self.store_code,
                        "source_product_ref": source_product_ref,
                        "image_url": image_url,
                        "current_price": float(current_price or 0),
                        "unit_price_value": float(unit_price_value) if unit_price_value is not None else None,
                        "unit_price_unit": unit_price_unit,
                        "promo_flag": promo_flag,
                        "promo_text": promo_text,
                    }
                ],
            }
        )
