# Маркетингова аналітика

Збір статистики з Facebook, Google та TikTok Ads через API з збереженням в SQLite.

## Структура

```
marketing_analytics/
├── data/
│   └── marketing.db      # SQLite база (створюється автоматично)
├── database/
│   ├── schema.sql        # Схема таблиць
│   └── db.py             # Робота з БД
├── collectors/
│   ├── facebook_collector.py
│   ├── google_collector.py
│   └── tiktok_collector.py
├── config.py
├── main.py
├── .env.example
└── requirements.txt
```

## Швидкий старт

```bash
cd marketing_analytics
pip install -r requirements.txt
cp .env.example .env
# Заповніть .env своїми API ключами

# Ініціалізувати БД
python main.py --init

# Зібрати дані (всі платформи, 7 днів)
python main.py

# Тільки Facebook за 30 днів
python main.py facebook --days 30
```

## Таблиці SQLite

| Таблиця | Опис |
|---------|------|
| `facebook_ads_daily` | Щоденна статистика Facebook Ads |
| `google_ads_daily` | Щоденна статистика Google Ads |
| `tiktok_ads_daily` | Щоденна статистика TikTok Ads |

## Корисні VIEW

```sql
-- Об'єднані дані всіх платформ
SELECT * FROM marketing_unified_daily;

-- Агрегати по платформах
SELECT * FROM platform_daily_totals;
```

## Приклад аналітики (SQL)

```sql
-- Загальний витрати по платформах за тиждень
SELECT 
    platform,
    SUM(total_spend) AS spend,
    SUM(total_conversions) AS conversions
FROM platform_daily_totals
WHERE date >= date('now', '-7 days')
GROUP BY platform;

-- Топ кампаній по ROI
SELECT 
    platform, campaign_name,
    SUM(cost) AS spend,
    SUM(conversion_value) AS revenue,
    SUM(conversion_value) - SUM(cost) AS profit
FROM marketing_unified_daily
GROUP BY platform, campaign_id, campaign_name
HAVING spend > 0
ORDER BY profit DESC;
```

## Отримання API ключів

- **Facebook**: [Business Manager](https://business.facebook.com) → Налаштування → Безпека → Токени доступу
- **Google Ads**: [Google Ads API](https://developers.google.com/google-ads/api/docs/get-started) — потрібна реєстрація розробника
- **TikTok**: [TikTok for Business](https://ads.tiktok.com) → Менеджер реклами → Інструменти → API

## Cron / автоматизація

Щоденний збір о 6:00:

```bash
0 6 * * * cd /path/to/marketing_analytics && python main.py --days 1
```
