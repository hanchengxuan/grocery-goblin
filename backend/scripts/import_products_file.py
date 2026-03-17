from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.catalog import upsert_product_record
from app.db import SessionLocal
from app.importers import load_import_records


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/import_products_file.py <path> [json]")
    path = Path(sys.argv[1]).resolve()
    source = sys.argv[2] if len(sys.argv) > 2 else "json"
    records = load_import_records(path, source=source)
    with SessionLocal() as db:
        for record in records:
            upsert_product_record(db, record)
    print(json.dumps({"imported": len(records), "path": str(path), "source": source}))


if __name__ == "__main__":
    main()
