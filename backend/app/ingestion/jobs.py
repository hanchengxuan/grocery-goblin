from datetime import datetime, timezone
from pathlib import Path
import json

from app.catalog import upsert_product_record
from app.db import SessionLocal
from app.importers.aldi import AldiImportSource
from app.storage import dated_raw_dir


def _write_raw_json(source: str, name: str, payload: dict | list) -> Path:
    target_dir = dated_raw_dir(source, datetime.now(timezone.utc))
    path = target_dir / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def ingest_aldi_category_tree(service_point: str = "G452") -> Path:
    src = AldiImportSource()
    payload = src.fetch_category_tree(service_point=service_point)
    return _write_raw_json("aldi", f"category_tree_{service_point}.json", payload)


def ingest_aldi_search_query(query: str, service_point: str = "G452", persist_to_db: bool = True) -> dict:
    src = AldiImportSource()
    payload = src.fetch_search_results(query, service_point=service_point)
    raw_path = _write_raw_json("aldi", f"search_{query.replace(' ', '_')}_{service_point}.json", payload)
    imported = 0
    if persist_to_db:
        records = src.load(raw_path)
        with SessionLocal() as db:
            for record in records:
                upsert_product_record(db, record)
                imported += 1
    return {
        "query": query,
        "service_point": service_point,
        "raw_path": str(raw_path),
        "result_count": len(payload.get("data", [])),
        "imported": imported,
    }
