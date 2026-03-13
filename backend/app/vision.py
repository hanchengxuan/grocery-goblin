from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import uuid

from .storage import dated_raw_dir

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

try:
    from pyzbar.pyzbar import decode as zbar_decode
except Exception:  # pragma: no cover
    zbar_decode = None

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None


BARCODE_RE = re.compile(r'(?:ean|upc|barcode)[-_ ]?(\d{8,14})', re.IGNORECASE)


def save_uploaded_image(temp_path: Path, filename: str | None = None) -> Path:
    suffix = Path(filename or temp_path.name).suffix or '.jpg'
    target_dir = dated_raw_dir('vision-uploads', datetime.now(timezone.utc))
    target = target_dir / f"{uuid.uuid4().hex}{suffix}"
    shutil.copy2(temp_path, target)
    return target


def decode_barcode_from_image(path: Path) -> tuple[str | None, str | None]:
    if Image is None or zbar_decode is None:
        return None, 'Barcode decoder dependencies are not installed'
    try:
        image = Image.open(path)
        decoded = zbar_decode(image)
        for item in decoded:
            text = item.data.decode('utf-8', errors='ignore').strip()
            if text:
                return text, None
        return None, None
    except Exception as exc:  # pragma: no cover
        return None, str(exc)


def extract_ocr_text_from_image(path: Path) -> tuple[str | None, str | None]:
    if Image is None or pytesseract is None:
        return None, 'OCR dependencies are not installed'
    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image).strip()
        if text:
            normalized = re.sub(r'\s+', ' ', text)
            return normalized[:500], None
        return None, None
    except Exception as exc:  # pragma: no cover
        return None, str(exc)


def derive_barcode_hint(filename: str) -> str | None:
    match = BARCODE_RE.search(filename)
    if match:
        return match.group(1)
    digits = ''.join(ch for ch in Path(filename).stem if ch.isdigit())
    if len(digits) in {8, 12, 13, 14}:
        return digits
    return None


def derive_query_hints_from_text(text: str | None) -> list[str]:
    if not text:
        return []
    cleaned = re.sub(r'[^a-z0-9]+', ' ', text.lower())
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


def derive_query_hints(filename: str) -> list[str]:
    return derive_query_hints_from_text(Path(filename).stem)


def derive_ocr_text(filename: str) -> str | None:
    stem = Path(filename).stem.lower()
    cleaned = re.sub(r'[^a-z0-9]+', ' ', stem).strip()
    return cleaned or None
