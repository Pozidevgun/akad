"""
Конфігурація — API ключі з змінних середовища.
Ніколи не зберігайте ключі в коді! Використовуйте .env файл.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Завантажити .env з папки marketing_analytics
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path)

# Facebook / Meta
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_AD_ACCOUNT_ID = os.getenv("FACEBOOK_AD_ACCOUNT_ID")  # формат: act_123456789

# Google Ads
GOOGLE_DEVELOPER_TOKEN = os.getenv("GOOGLE_DEVELOPER_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
GOOGLE_CUSTOMER_ID = os.getenv("GOOGLE_CUSTOMER_ID")  # без дефісів, напр. 1234567890

# TikTok
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
TIKTOK_ADVERTISER_ID = os.getenv("TIKTOK_ADVERTISER_ID")


def validate_config(platform: str) -> bool:
    """Перевірка наявності необхідних credentials для платформи."""
    required = {
        "facebook": [FACEBOOK_ACCESS_TOKEN, FACEBOOK_AD_ACCOUNT_ID],
        "google": [
            GOOGLE_DEVELOPER_TOKEN,
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            GOOGLE_REFRESH_TOKEN,
            GOOGLE_CUSTOMER_ID,
        ],
        "tiktok": [TIKTOK_ACCESS_TOKEN, TIKTOK_ADVERTISER_ID],
    }
    values = required.get(platform, [])
    return all(v for v in values)
