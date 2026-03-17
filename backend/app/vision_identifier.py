import base64
import json
import re
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


class _JsonRecoveryMixin:
    def _extract_json_object(self, text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?', '', cleaned).strip()
            cleaned = re.sub(r'```$', '', cleaned).strip()
        first_brace = cleaned.find('{')
        if first_brace > 0:
            cleaned = cleaned[first_brace:]
        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r'\{.*\}', cleaned, re.S)
            if match:
                candidate = match.group(0)
                try:
                    return json.loads(candidate)
                except Exception:
                    recovered = self._recover_partial_fields(candidate)
                    if recovered:
                        return recovered
            recovered = self._recover_partial_fields(cleaned)
            if recovered:
                return recovered
            raise

    def _recover_partial_fields(self, text: str) -> dict | None:
        fields: dict[str, object] = {}
        str_patterns = {
            'name': r'"name"\s*:\s*"([^"]*)',
            'brand': r'"brand"\s*:\s*"([^"]*)',
            'size_label': r'"size_label"\s*:\s*"([^"]*)',
            'category': r'"category"\s*:\s*"([^"]*)',
            'barcode': r'"barcode"\s*:\s*"([^"]*)',
            'raw_text': r'"raw_text"\s*:\s*"([^"]*)',
        }
        for key, pattern in str_patterns.items():
            m = re.search(pattern, text, re.S)
            if m:
                fields[key] = m.group(1)
            elif re.search(rf'"{key}"\s*:\s*null', text):
                fields[key] = None
        m = re.search(r'"confidence"\s*:\s*([0-9]+(?:\.[0-9]+)?)', text)
        if m:
            fields['confidence'] = float(m.group(1))
        elif re.search(r'"confidence"\s*:\s*null', text):
            fields['confidence'] = 0.0
        if any(k in fields for k in ('name', 'brand', 'size_label', 'category', 'barcode', 'raw_text', 'confidence')):
            fields.setdefault('confidence', 0.0)
            return fields
        return None


class OpenAICompatibleVisionProvider(_JsonRecoveryMixin):
    def __init__(self, *, provider_name: str, api_key: str, base_url: str, model: str, timeout_seconds: int = 120):
        self.provider_name = provider_name
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.last_error: str | None = None
        self.last_response_preview: str | None = None

    def identify(self, image_path: Path) -> VisionIdentification | None:
        self.last_error = None
        self.last_response_preview = None
        mime = 'image/jpeg'
        if image_path.suffix.lower() == '.png':
            mime = 'image/png'
        elif image_path.suffix.lower() == '.webp':
            mime = 'image/webp'
        image_b64 = base64.b64encode(image_path.read_bytes()).decode('utf-8')
        prompt = (
            'Identify the grocery product in this image. '
            'Return JSON only with keys: name, brand, size_label, category, barcode, confidence. '
            'Each value should be short. Keep confidence between 0 and 1. Use null when unknown. '
            'Do not say anything before the JSON. Start the response with { and end with }.'
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
            'max_tokens': 120,
            'stream': False,
        }
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        try:
            timeout = httpx.Timeout(connect=20, read=self.timeout_seconds, write=30, pool=30)
            with httpx.Client(timeout=timeout) as client:
                response = client.post(f'{self.base_url}/chat/completions', headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            text = data['choices'][0]['message']['content']
            if isinstance(text, list):
                text = ''.join(part.get('text', '') for part in text if isinstance(part, dict))
            self.last_response_preview = str(text)[:1200]
            obj = self._extract_json_object(str(text))
            return VisionIdentification(
                provider=self.provider_name,
                name=obj.get('name'),
                brand=obj.get('brand'),
                size_label=obj.get('size_label'),
                category=obj.get('category'),
                barcode=obj.get('barcode'),
                confidence=float(obj.get('confidence') or 0),
                raw_text=None,
            )
        except Exception as exc:
            self.last_error = str(exc)
            return None


class GeminiVisionProvider(_JsonRecoveryMixin):
    def __init__(self, *, api_key: str, model: str, timeout_seconds: int = 120):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.last_error: str | None = None
        self.last_response_preview: str | None = None

    def identify(self, image_path: Path) -> VisionIdentification | None:
        self.last_error = None
        self.last_response_preview = None
        mime = 'image/jpeg'
        if image_path.suffix.lower() == '.png':
            mime = 'image/png'
        elif image_path.suffix.lower() == '.webp':
            mime = 'image/webp'
        image_b64 = base64.b64encode(image_path.read_bytes()).decode('utf-8')
        prompt = (
            'Extract grocery product information from this image. '
            'Only identify the main retail product visible on the package front. '
            'Return only JSON matching the provided schema. '
            'Use null for unknown values. Keep name complete and concise.'
        )
        payload = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [
                        {'text': prompt},
                        {'inline_data': {'mime_type': mime, 'data': image_b64}},
                    ],
                }
            ],
            'generationConfig': {
                'temperature': 0,
                'responseMimeType': 'application/json',
                'responseSchema': {
                    'type': 'OBJECT',
                    'required': ['name', 'brand', 'size_label', 'category'],
                    'properties': {
                        'name': {'type': 'STRING', 'description': 'Complete product name visible on the front of pack.'},
                        'brand': {'type': 'STRING', 'nullable': True, 'description': 'Brand name.'},
                        'size_label': {'type': 'STRING', 'nullable': True, 'description': 'Pack size like 450g or 2L.'},
                        'category': {'type': 'STRING', 'nullable': True, 'description': 'Simple grocery category such as cereal, dairy, snack.'},
                    },
                    'propertyOrdering': ['name', 'brand', 'size_label', 'category'],
                },
                'maxOutputTokens': 120,
                'thinkingConfig': {'thinkingBudget': 0},
            },
        }
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}'
        try:
            timeout = httpx.Timeout(connect=20, read=self.timeout_seconds, write=30, pool=30)
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            self.last_response_preview = str(text)[:1200]
            obj = self._extract_json_object(str(text))
            name = obj.get('name')
            return VisionIdentification(
                provider='gemini',
                name=name,
                brand=obj.get('brand'),
                size_label=obj.get('size_label'),
                category=obj.get('category'),
                barcode=None,
                confidence=0.85 if name else 0.0,
                raw_text=None,
            )
        except Exception as exc:
            self.last_error = str(exc)
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
            timeout_seconds=settings.vision_timeout_seconds,
        )
    if provider == 'gemini' and settings.gemini_api_key:
        return GeminiVisionProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_vision_model,
            timeout_seconds=settings.vision_timeout_seconds,
        )
    if provider in {'nvidia_nim', 'nvidia_nim_kimi', 'kimi'} and settings.nvidia_nim_api_key and settings.nvidia_nim_base_url and settings.nvidia_nim_vision_model:
        return OpenAICompatibleVisionProvider(
            provider_name='nvidia_nim',
            api_key=settings.nvidia_nim_api_key,
            base_url=settings.nvidia_nim_base_url,
            model=settings.nvidia_nim_vision_model,
            timeout_seconds=settings.vision_timeout_seconds,
        )
    return PlaceholderVisionProvider()


def identify_product_from_image(image_path: Path) -> VisionIdentification | None:
    provider = get_vision_provider()
    return provider.identify(image_path)
