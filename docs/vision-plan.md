# Grocery Goblin — Vision Plan

## Goal
Support product lookup from a user photo using:
1. **Barcode-first detection**
2. **Vision model identification**
3. **OCR fallback**
4. Search-based candidate confirmation

## Current state
- Upload endpoint exists: `/vision/identify-product`
- Uploaded images are stored under `/data/grocery-goblin/raw/vision-uploads/...`
- Product model supports canonical `barcode`
- Barcode-first flow is wired in API logic
- OCR fallback is currently placeholder text extraction from filename

## Real barcode stack
### Preferred local path
- Python: `pyzbar`
- System library: `libzbar`
- Image loader: `Pillow`

## Required host packages
On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y libzbar0 zbar-tools
```

Then in backend venv:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## OCR next step
Current code path is wired for `pytesseract`, but the host still needs the `tesseract` binary.

Possible options:
- Tesseract (local, cheap)
- PaddleOCR
- Cloud vision model

### Required host package for current OCR path
```bash
sudo apt update
sudo apt install -y tesseract-ocr
```

## Recommended sequence
1. Enable real barcode decoding with `libzbar`
2. Validate end-to-end barcode photo lookup
3. Add real OCR fallback
4. Improve product matching/ranking
