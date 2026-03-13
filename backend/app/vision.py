from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import uuid

from .storage import dated_raw_dir


BARCODE_RE = re.compile(r'(?:ean|upc|barcode)[-_ ]?(\d{8,14})', re.IGNORECASE)


def save_uploaded_image(temp_path: Path, filename: str | None = None) -> Path:
    suffix = Path(filename or temp_path.name).suffix or '.jpg'
    target_dir = dated_raw_dir('vision-uploads', datetime.now(timezone.utc))
    target = target_dir / f"{uuid.uuid4().hex}{suffix}"
    shutil.copy2(temp_path, target)
    return target


def derive_barcode_hint(filename: str) -> str | None:
    match = BARCODE_RE.search(filename)
    if match:
        return match.group(1)
    digits = ''.join(ch for ch in Path(filename).stem if ch.isdigit())
    if len(digits) in {8, 12, 13, 14}:
        return digits
    return None


def derive_query_hints(filename: str) -> list[str]:
    stem = Path(filename).stem.lower()
    cleaned = re.sub(r'[^a-z0-9]+', ' ', stem)
    tokens = [tok for tok in cleaned.split() if tok and tok not in {'img', 'image', 'photo', 'scan', 'upload', 'ean', 'upc', 'barcode'} and not tok.isdigit()]
    if not tokens:
        return []
    hints = []
    if 'milk' in tokens:
        hints.append('milk')
        if 'full' in tokens and 'cream' in tokens:
            hints.append('full cream milk')
    if 'banana' in tokens or 'bananas' in tokens:
        hints.append('banana')
    if not hints:
        hints.append(' '.join(tokens[:3]))
    return list(dict.fromkeys(hints))


def derive_ocr_text(filename: str) -> str | None:
    stem = Path(filename).stem.lower()
    cleaned = re.sub(r'[^a-z0-9]+', ' ', stem).strip()
    return cleaned or None
