from __future__ import annotations

"""AI page package."""

from .content_factory_page import AIContentFactoryPage
from .copy_generation_page import CopyGenerationPage
from .creative_workshop_page import CreativeWorkshopPage
from .page import AIPage
from .product_title_page import ProductTitlePage
from .script_extractor_page import ScriptExtractorPage
from .viral_title_page import ViralTitlePage

__all__ = [
    "AIContentFactoryPage",
    "AIPage",
    "CopyGenerationPage",
    "CreativeWorkshopPage",
    "ProductTitlePage",
    "ScriptExtractorPage",
    "ViralTitlePage",
]
