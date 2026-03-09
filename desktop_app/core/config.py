import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    app_name: str = "TK-OPS TikTok Shop Desktop"
    openai_api_key: str | None = None
    tiktok_api_key: str | None = None
    tiktok_api_secret: str | None = None
    data_path: str = os.path.expanduser("~/.tkops/desktop")

def load_config() -> AppConfig:
    # Read environment variables; fallback to None so OpenAI can be disabled gracefully
    return AppConfig(
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        tiktok_api_key=os.environ.get("TIKTOK_API_KEY"),
        tiktok_api_secret=os.environ.get("TIKTOK_API_SECRET"),
        data_path=os.environ.get("TKOPS_DATA_PATH", os.path.expanduser("~/.tkops/desktop")),
    )
