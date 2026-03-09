from typing import List
from desktop_app.ai.openai_client import OpenAIClient
from desktop_app.tiktok.api_client import TikTokShopClient
from desktop_app.db import create_session, get_engine
from desktop_app.models import CopyDraft, Product, Campaign


class Pipeline:
    def __init__(self, ai_client: OpenAIClient, tiktok_client: TikTokShopClient):
        self.ai = ai_client
        self.tiktok = tiktok_client
        self.engine = get_engine()
        self.Session = create_session(self.engine)

    def run_product_selection(self, query: str = "") -> List[Product]:
        # In MVP, fetch from TikTokShop client (or mock data)
        return self.tiktok.fetch_products(query=query)

    def run_copy_generation(self, product: Product, prompt_template: str) -> CopyDraft:
        # Build a prompt and fetch copy text from AI
        prompt = prompt_template.format(title=product.title, description=product.description)
        content = self.ai.complete(prompt)
        draft = CopyDraft(id=1, product_id=product.id, title=product.title, content=content)
        return draft

    def run_campaign(self, product: Product, copy: CopyDraft) -> Campaign:
        # Create a simple campaign placeholder
        return Campaign(id=1, name=f"Campaign for {product.title}", product_id=product.id, status="Scheduled")
