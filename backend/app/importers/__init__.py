from pathlib import Path

from .aldi import AldiImportSource
from .base import ImportSource, JsonFileImportSource, ProductImportRecord, SupermarketImportSource
from .coles import ColesImportSource
from .woolworths import WoolworthsImportSource

IMPORTER_REGISTRY = {
    "json": JsonFileImportSource,
    "woolworths": WoolworthsImportSource,
    "coles": ColesImportSource,
    "aldi": AldiImportSource,
}


def load_import_records(path: Path, source: str = "json"):
    source = source.lower().strip()
    cls = IMPORTER_REGISTRY.get(source)
    if not cls:
        raise ValueError(f"Unsupported import source: {source}")
    return cls().load(path)


__all__ = [
    "ImportSource",
    "JsonFileImportSource",
    "SupermarketImportSource",
    "WoolworthsImportSource",
    "ColesImportSource",
    "AldiImportSource",
    "IMPORTER_REGISTRY",
    "load_import_records",
]
