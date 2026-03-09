from dataclasses import dataclass
from typing import List, Optional

from desktop_app.models import Product


@dataclass
class TikTokShopClient:
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

    def fetch_products(self, query: Optional[str] = None) -> List[Product]:
        # Placeholder: In MVP we return mock data; real implementation should call TikTok Shop API
        mock = [
            Product(id=1, title="样板产品 A", description="描述 A", price=9.99, category="样例"),
            Product(id=2, title="样板产品 B", description="描述 B", price=19.99, category="样例"),
        ]
        return mock
