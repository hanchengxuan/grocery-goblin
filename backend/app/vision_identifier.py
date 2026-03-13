from pathlib import Path
from typing import Protocol

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


def identify_product_from_image(image_path: Path) -> VisionIdentification | None:
    provider = PlaceholderVisionProvider()
    return provider.identify(image_path)
