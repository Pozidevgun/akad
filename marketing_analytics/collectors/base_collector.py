"""
Базовий клас для колекторів. Всі колектори наслідують від нього.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class BaseCollector(ABC):
    """Абстрактний колектор зі статистики реклами."""

    def __init__(self, date_from: datetime = None, date_to: datetime = None):
        self.date_from = date_from or datetime.now() - timedelta(days=7)
        self.date_to = date_to or datetime.now()

    @abstractmethod
    def fetch(self) -> list[dict]:
        """
        Отримати дані з API.
        Повертає список словників, готових для вставки в відповідну таблицю.
        """
        pass

    @abstractmethod
    def get_table_name(self) -> str:
        """Назва таблиці в БД для цього колектора."""
        pass

    @abstractmethod
    def get_columns(self) -> list[str]:
        """Список колонок для INSERT."""
        pass
