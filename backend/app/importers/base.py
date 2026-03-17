from pathlib import Path
import json

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


def load_import_records(path: Path, source: str = "json") -> list[ProductImportRecord]:
    if source == "json":
        return JsonFileImportSource().load(path)
    raise ValueError(f"Unsupported import source: {source}")
