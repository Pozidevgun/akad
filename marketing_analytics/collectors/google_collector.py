"""
Колектор для Google Ads API.
Документація: https://developers.google.com/google-ads/api/docs/start
"""
from datetime import datetime
from typing import Optional

from .base_collector import BaseCollector

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleCollector(BaseCollector):
    """Збір даних з Google Ads API."""

    def __init__(
        self,
        client_config: dict,
        customer_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ):
        super().__init__(date_from, date_to)
        self.client_config = client_config
        self.customer_id = customer_id.replace("-", "")

    def get_table_name(self) -> str:
        return "google_ads_daily"

    def get_columns(self) -> list[str]:
        return [
            "date", "customer_id", "campaign_id", "campaign_name",
            "ad_group_id", "ad_group_name",
            "impressions", "clicks", "cost", "conversions", "conversion_value",
            "ctr", "avg_cpc", "avg_cpm"
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

    def fetch(self) -> list[dict]:
        if not GOOGLE_AVAILABLE:
            raise ImportError("Встановіть: pip install google-ads")

        client = GoogleAdsClient.load_from_dict(self.client_config)

        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                segments.date,
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.average_cpm
            FROM ad_group
            WHERE segments.date BETWEEN '{self.date_from.strftime("%Y-%m-%d")}'
                AND '{self.date_to.strftime("%Y-%m-%d")}'
                AND campaign.status = 'ENABLED'
            ORDER BY segments.date
        """

        rows = []
        try:
            response = ga_service.search_stream(customer_id=self.customer_id, query=query)
            for batch in response:
                for row in batch.results:
                    segment = row.segments
                    campaign = row.campaign
                    ad_group = row.ad_group
                    m = row.metrics
                    rows.append({
                        "date": segment.date,
                        "customer_id": self.customer_id,
                        "campaign_id": str(campaign.id) if campaign.id else "",
                        "campaign_name": campaign.name or "",
                        "ad_group_id": str(ad_group.id) if ad_group.id else "",
                        "ad_group_name": ad_group.name or "",
                        "impressions": self._safe_int(m.impressions),
                        "clicks": self._safe_int(m.clicks),
                        "cost": self._safe_float(m.cost_micros) / 1_000_000 if m.cost_micros else 0,
                        "conversions": self._safe_float(m.conversions),
                        "conversion_value": self._safe_float(m.conversions_value),
                        "ctr": self._safe_float(m.ctr),
                        "avg_cpc": self._safe_float(m.average_cpc) / 1_000_000 if m.average_cpc else 0,
                        "avg_cpm": self._safe_float(m.average_cpm) / 1_000 if m.average_cpm else 0,
                    })
        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                print(f"Google Ads помилка: {error.message}")
            raise
        return rows
