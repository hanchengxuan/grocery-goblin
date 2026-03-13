import base64
from pathlib import Path
from typing import Protocol

import httpx

from .config import get_settings
from .schemas import VisionIdentification


class VisionProvider(Protocol):
    def identify(self, image_path: Path) -> VisionIdentification | None: ...


class PlaceholderVisionProvider:
    name = 'placeholder'

    def identify(self, image_path: Path) -> VisionIdentification | None:
        stem = image_path.stem.lower()
        if 'milk' in stem:
            return VisionIdentification(
                provider=self.name,
                name='Full Cream Milk',
                brand='Generic',
                size_label='2L',
                category='dairy',
                confidence=0.35,
                raw_text=stem,
            )
        if 'banana' in stem:
            return VisionIdentification(
                provider=self.name,
                name='Bananas',
                category='fruit',
                confidence=0.3,
                raw_text=stem,
            )
        return None


class OpenAICompatibleVisionProvider:
    def __init__(self, *, provider_name: str, api_key: str, base_url: str, model: str):
        self.provider_name = provider_name
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model

    def identify(self, image_path: Path) -> VisionIdentification | None:
        mime = 'image/jpeg'
        if image_path.suffix.lower() == '.png':
            mime = 'image/png'
        elif image_path.suffix.lower() == '.webp':
            mime = 'image/webp'
        image_b64 = base64.b64encode(image_path.read_bytes()).decode('utf-8')
        prompt = (
            'Identify this grocery product and return a compact JSON object with keys: '
            'name, brand, size_label, category, barcode, confidence, raw_text. '
            'If unknown, use nulls and low confidence. Output JSON only.'
        )
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{image_b64}'}},
                    ],
                }
            ],
            'temperature': 0,
        }
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(f'{self.base_url}/chat/completions', headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            text = data['choices'][0]['message']['content']
            if isinstance(text, list):
                text = ''.join(part.get('text', '') for part in text if isinstance(part, dict))
            import json
            obj = json.loads(text)
            return VisionIdentification(
                provider=self.provider_name,
                name=obj.get('name'),
                brand=obj.get('brand'),
                size_label=obj.get('size_label'),
                category=obj.get('category'),
                barcode=obj.get('barcode'),
                confidence=float(obj.get('confidence') or 0),
                raw_text=obj.get('raw_text'),
            )
        except Exception:
            return None


def get_vision_provider() -> VisionProvider:
    settings = get_settings()
    provider = settings.vision_provider.lower().strip()
    if provider == 'openai' and settings.openai_api_key:
        return OpenAICompatibleVisionProvider(
            provider_name='openai',
            api_key=settings.openai_api_key,
            base_url='https://api.openai.com/v1',
            model=settings.openai_vision_model,
        )
    if provider in {'nvidia_nim', 'nvidia_nim_kimi', 'kimi'} and settings.nvidia_nim_api_key and settings.nvidia_nim_base_url and settings.nvidia_nim_vision_model:
        return OpenAICompatibleVisionProvider(
            provider_name='nvidia_nim',
            api_key=settings.nvidia_nim_api_key,
            base_url=settings.nvidia_nim_base_url,
            model=settings.nvidia_nim_vision_model,
        )
    return PlaceholderVisionProvider()


def identify_product_from_image(image_path: Path) -> VisionIdentification | None:
    provider = get_vision_provider()
    return provider.identify(image_path)
