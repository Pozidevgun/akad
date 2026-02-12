"""
Головний скрипт для збору маркетингової статистики.
Запуск: python main.py [platform] [--days N]

Приклади:
  python main.py              # всі платформи, останні 7 днів
  python main.py facebook     # тільки Facebook
  python main.py google --days 30
"""
import argparse
from datetime import datetime, timedelta

from config import (
    FACEBOOK_ACCESS_TOKEN,
    FACEBOOK_AD_ACCOUNT_ID,
    GOOGLE_DEVELOPER_TOKEN,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REFRESH_TOKEN,
    GOOGLE_CUSTOMER_ID,
    TIKTOK_ACCESS_TOKEN,
    TIKTOK_ADVERTISER_ID,
)
from database import init_database, execute_many
from collectors import FacebookCollector, GoogleCollector, TikTokCollector


def run_collector(platform: str, days: int):
    """Запустити колектор і зберегти дані в БД."""
    date_to = datetime.now()
    date_from = date_to - timedelta(days=days)

    if platform == "facebook":
        if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_AD_ACCOUNT_ID:
            print("⚠ Пропущено Facebook: додайте FACEBOOK_ACCESS_TOKEN та FACEBOOK_AD_ACCOUNT_ID в .env")
            return 0
        coll = FacebookCollector(FACEBOOK_ACCESS_TOKEN, FACEBOOK_AD_ACCOUNT_ID, date_from, date_to)
    elif platform == "google":
        if not all([GOOGLE_DEVELOPER_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, GOOGLE_CUSTOMER_ID]):
            print("⚠ Пропущено Google: додайте всі GOOGLE_* змінні в .env")
            return 0
        config = {
            "developer_token": GOOGLE_DEVELOPER_TOKEN,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": GOOGLE_REFRESH_TOKEN,
            "use_proto_plus": True,
        }
        coll = GoogleCollector(config, GOOGLE_CUSTOMER_ID, date_from, date_to)
    elif platform == "tiktok":
        if not TIKTOK_ACCESS_TOKEN or not TIKTOK_ADVERTISER_ID:
            print("⚠ Пропущено TikTok: додайте TIKTOK_ACCESS_TOKEN та TIKTOK_ADVERTISER_ID в .env")
            return 0
        coll = TikTokCollector(TIKTOK_ACCESS_TOKEN, TIKTOK_ADVERTISER_ID, date_from, date_to)
    else:
        raise ValueError(f"Невідома платформа: {platform}")

    rows = coll.fetch()
    if rows:
        n = execute_many(coll.get_table_name(), coll.get_columns(), rows)
        print(f"  ✓ {platform}: збережено {n} записів")
    else:
        print(f"  ○ {platform}: немає даних за період")
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Збір маркетингової статистики в SQLite")
    parser.add_argument(
        "platform",
        nargs="?",
        choices=["facebook", "google", "tiktok", "all"],
        default="all",
        help="Платформа для збору (за замовчуванням: всі)",
    )
    parser.add_argument("--days", type=int, default=7, help="Кількість днів для збору (за замовчуванням: 7)")
    parser.add_argument("--init", action="store_true", help="Тільки ініціалізувати БД (створити таблиці)")
    args = parser.parse_args()

    init_database()

    if args.init:
        print("База даних готова.")
        return

    platforms = ["facebook", "google", "tiktok"] if args.platform == "all" else [args.platform]
    print(f"Збір даних за останні {args.days} днів: {', '.join(platforms)}")

    for p in platforms:
        try:
            run_collector(p, args.days)
        except Exception as e:
            print(f"  ✗ {p}: помилка — {e}")

    print("Готово.")


if __name__ == "__main__":
    main()
