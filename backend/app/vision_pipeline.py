from pathlib import Path

from sqlalchemy.orm import Session

from .catalog import search_products_by_barcode, search_products_grouped
from .schemas import GroupedProductSearchResult, VisionIdentifyResponse
from .vision import (
    decode_barcode_from_image,
    derive_barcode_hint,
    derive_ocr_text,
    derive_query_hints,
    derive_query_hints_from_text,
    extract_ocr_text_from_image,
)
from .vision_identifier import identify_product_from_image


def run_vision_pipeline(db: Session, saved_path: Path, original_filename: str | None = None) -> VisionIdentifyResponse:
    source_name = original_filename or saved_path.name

    decoded_barcode, decode_error = decode_barcode_from_image(saved_path)
    filename_barcode = derive_barcode_hint(source_name)
    barcode = decoded_barcode or filename_barcode
    if decoded_barcode:
        barcode_status = 'decoded_from_image'
    elif filename_barcode:
        barcode_status = 'derived_from_filename'
    elif decode_error:
        barcode_status = f'barcode_decoder_unavailable: {decode_error}'
    else:
        barcode_status = 'no_barcode_detected'

    extracted_ocr_text, ocr_error = extract_ocr_text_from_image(saved_path)
    fallback_ocr_text = derive_ocr_text(source_name)
    ocr_text = extracted_ocr_text or fallback_ocr_text
    if extracted_ocr_text:
        ocr_status = 'extracted_from_image'
    elif fallback_ocr_text:
        ocr_status = 'derived_from_filename'
    elif ocr_error:
        ocr_status = f'ocr_unavailable: {ocr_error}'
    else:
        ocr_status = 'no_ocr_text_detected'

    vision_result = identify_product_from_image(saved_path)
    vision_status = 'identified' if vision_result else 'no_vision_match'

    hints = []
    if vision_result:
        for candidate in [vision_result.name, f"{vision_result.brand or ''} {vision_result.name or ''}".strip(), vision_result.size_label]:
            if candidate:
                hints.extend(derive_query_hints_from_text(candidate))
    hints = hints or derive_query_hints_from_text(ocr_text) or derive_query_hints(source_name)
    hints = list(dict.fromkeys([h for h in hints if h]))

    matches: list[GroupedProductSearchResult] = []
    if barcode:
        matches = search_products_by_barcode(db, barcode)
    if not matches:
        for hint in hints:
            results = search_products_grouped(db, hint)
            if results:
                matches = results
                break

    return VisionIdentifyResponse(
        uploaded_path=str(saved_path),
        barcode=barcode,
        barcode_status=barcode_status,
        ocr_text=ocr_text,
        ocr_status=ocr_status,
        vision=vision_result,
        vision_status=vision_status,
        query_hints=hints,
        matches=matches,
    )
