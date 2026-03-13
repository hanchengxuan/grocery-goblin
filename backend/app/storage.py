from pathlib import Path
from datetime import datetime, timezone

DATA_ROOT = Path('/data/grocery-goblin')
RAW_ROOT = DATA_ROOT / 'raw'
LOG_ROOT = DATA_ROOT / 'logs'
CACHE_ROOT = DATA_ROOT / 'cache'
EXPORT_ROOT = DATA_ROOT / 'exports'


for path in (RAW_ROOT, LOG_ROOT, CACHE_ROOT, EXPORT_ROOT):
    path.mkdir(parents=True, exist_ok=True)


def dated_raw_dir(source: str, when: datetime | None = None) -> Path:
    stamp = (when or datetime.now(timezone.utc)).strftime('%Y-%m-%d')
    target = RAW_ROOT / source / stamp
    target.mkdir(parents=True, exist_ok=True)
    return target
