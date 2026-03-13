from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import SessionLocal
from app.seed import seed_reference_data


def main() -> None:
    with SessionLocal() as db:
        seed_reference_data(db)
        print("seeded reference data")


if __name__ == "__main__":
    main()
