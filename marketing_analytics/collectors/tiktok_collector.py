"""
Колектор для TikTok Marketing API.
Документація: https://business-api.tiktok.com/portal/docs
"""
from datetime import datetime
from typing import Optional

import requests

from .base_collector import BaseCollector


class TikTokCollector(BaseCollector):
    """Збір даних з TikTok Marketing API."""

    BASE_URL = "https://business-api.tiktok.com/open_api/v1.3"

    def __init__(
        self,
        access_token: str,
        advertiser_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ):
        super().__init__(date_from, date_to)
        self.access_token = access_token
        self.advertiser_id = advertiser_id

    def get_table_name(self) -> str:
        return "tiktok_ads_daily"

    def get_columns(self) -> list[str]:
        return [
            "date", "advertiser_id", "campaign_id", "campaign_name",
            "adgroup_id", "adgroup_name", "ad_id",
            "impressions", "clicks", "spend", "reach",
            "conversions", "conversion_value", "cpm", "cpc", "ctr"
        ]

    def _safe_float(self, val, default=0):
        try:
            return float(val) if val is not None else default
        except (TypeError, ValueError):
            return default

    def _safe_int(self, val, default=0):
        try:
            return int(val) if val is not None else default
        except (TypeError, ValueError):
            return default

    def _request(self, endpoint: str, params: dict) -> dict:
        """Виконати запит до TikTok API."""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Access-Token": self.access_token, "Content-Type": "application/json"}
        resp = requests.post(url, json=params, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def fetch(self) -> list[dict]:
        params = {
            "advertiser_id": self.advertiser_id,
            "report_type": "BASIC",
            "dimensions": ["stat_time_day", "campaign_id", "adgroup_id", "ad_id"],
            "metrics": [
                "spend", "impressions", "clicks", "reach",
                "conversion", "total_purchase_value",
                "ctr", "cpc", "cpm"
            ],
            "data_level": "AUCTION_AD",
            "start_date": self.date_from.strftime("%Y-%m-%d"),
            "end_date": self.date_to.strftime("%Y-%m-%d"),
        }

        data = self._request("report/integrated/get/", params)
        rows = []

        if data.get("code") != 0:
            raise RuntimeError(f"TikTok API помилка: {data.get('message', data)}")

        list_data = data.get("data", {}).get("list", [])
        for item in list_data:
            metrics = item.get("metrics", {})
            dimensions = item.get("dimensions", {})
            rows.append({
                "date": dimensions.get("stat_time_day", ""),
                "advertiser_id": self.advertiser_id,
                "campaign_id": dimensions.get("campaign_id", ""),
                "campaign_name": dimensions.get("campaign_name", ""),
                "adgroup_id": dimensions.get("adgroup_id", ""),
                "adgroup_name": dimensions.get("adgroup_name", ""),
                "ad_id": dimensions.get("ad_id", ""),
                "impressions": self._safe_int(metrics.get("impressions")),
                "clicks": self._safe_int(metrics.get("clicks")),
                "spend": self._safe_float(metrics.get("spend")),
                "reach": self._safe_int(metrics.get("reach")),
                "conversions": self._safe_int(metrics.get("conversion")),
                "conversion_value": self._safe_float(metrics.get("total_purchase_value")),
                "cpm": self._safe_float(metrics.get("cpm")),
                "cpc": self._safe_float(metrics.get("cpc")),
                "ctr": self._safe_float(metrics.get("ctr")),
            })
        return rows
