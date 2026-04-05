from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.importers.aldi import AldiImportSource


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/fetch_aldi_search.py <query> [output_path]")
    query = sys.argv[1]
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data" / f"aldi_search_{query.replace(' ', '_')}.json"
    src = AldiImportSource()
    payload = src.fetch_search_results(query)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"query": query, "output_path": str(output_path), "count": len(payload.get('data', []))}))


if __name__ == "__main__":
    main()
