import os
try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


class OpenAIClient:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        if openai is not None and self.api_key:
            openai.api_key = self.api_key

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        if openai is None or not self.api_key:
            return "[AI] OpenAI not configured. Provide OPENAI_API_KEY."
        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return resp.choices[0].message["content"].strip()
        except Exception as e:
            return f"[AI] Error: {e}"
