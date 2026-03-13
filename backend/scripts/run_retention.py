from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import SessionLocal
from app.pricing import purge_old_snapshots, rollup_daily_snapshots


def main() -> None:
    with SessionLocal() as db:
        rolled = rollup_daily_snapshots(db, older_than_days=0)
        purged = purge_old_snapshots(db, retention_days=30)
        print({"rolled_daily_aggregates": rolled, "purged_snapshots": purged})


if __name__ == "__main__":
    main()
