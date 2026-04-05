from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ingestion.jobs import ingest_aldi_category_tree, ingest_aldi_search_query


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/ingest_aldi.py category-tree | search <query>")
    command = sys.argv[1]
    if command == "category-tree":
        path = ingest_aldi_category_tree()
        print(json.dumps({"category_tree_path": str(path)}))
        return
    if command == "search":
        if len(sys.argv) < 3:
            raise SystemExit("Usage: python scripts/ingest_aldi.py search <query>")
        result = ingest_aldi_search_query(' '.join(sys.argv[2:]))
        print(json.dumps(result))
        return
    raise SystemExit(f"Unknown command: {command}")
