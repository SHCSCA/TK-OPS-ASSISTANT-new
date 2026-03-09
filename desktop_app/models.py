from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Product:
    id: int
    title: str
    description: str
    price: float
    image_url: str | None = None
    category: str = "Unknown"
    external_id: Optional[str] = None
    created_at: datetime | None = None


@dataclass
class CopyDraft:
    id: int
    product_id: int
    title: str
    content: str
    language: str = "en"
    tone: str = "neutral"
    created_at: datetime | None = None


@dataclass
class Campaign:
    id: int
    name: str
    product_id: int
    status: str
    scheduled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
