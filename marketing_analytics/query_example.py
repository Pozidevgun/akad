#!/usr/bin/env python3
"""
Приклад SQL-запитів для маркетингової аналітики.
Запуск: python3 query_example.py
"""
from database import init_database, execute_query


def run_queries():
    init_database()

    # 1. Об'єднані дані (всі платформи)
    print("\n--- marketing_unified_daily (останні 10 записів) ---")
    rows = execute_query("""
        SELECT * FROM marketing_unified_daily 
        ORDER BY date DESC, platform 
        LIMIT 10
    """)
    for r in rows:
        print(r)

    # 2. Сумарні витрати по платформах
    print("\n--- platform_daily_totals ---")
    rows = execute_query("SELECT * FROM platform_daily_totals ORDER BY date DESC LIMIT 15")
    for r in rows:
        print(r)

    # 3. Загальна сума витрат за тиждень
    print("\n--- Загальні витрати за 7 днів ---")
    rows = execute_query("""
        SELECT platform, 
               SUM(total_spend) AS total_spend,
               SUM(total_conversions) AS conversions
        FROM platform_daily_totals
        WHERE date >= date('now', '-7 days')
        GROUP BY platform
    """)
    for r in rows:
        print(r)


if __name__ == "__main__":
    run_queries()
