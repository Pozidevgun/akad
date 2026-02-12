"""
Колектор для Facebook / Meta Ads API.
Документація: https://developers.facebook.com/docs/marketing-apis
"""
from datetime import datetime
from typing import Optional

from .base_collector import BaseCollector

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adsinsights import AdsInsights
    FACEBOOK_AVAILABLE = True
except ImportError:
    FACEBOOK_AVAILABLE = False


class FacebookCollector(BaseCollector):
    """Збір даних з Facebook Marketing API."""

    def __init__(
        self,
        access_token: str,
        ad_account_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ):
        super().__init__(date_from, date_to)
        self.access_token = access_token
        self.ad_account_id = ad_account_id.replace("act_", "") if ad_account_id.startswith("act_") else ad_account_id

    def get_table_name(self) -> str:
        return "facebook_ads_daily"

    def get_columns(self) -> list[str]:
        return [
            "date", "account_id", "campaign_id", "campaign_name",
            "adset_id", "adset_name", "ad_id", "ad_name",
            "impressions", "clicks", "spend", "reach",
            "cpm", "cpc", "ctr", "conversions", "conversion_value"
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

    def _parse_insight(self, insight: dict) -> dict:
        """Перетворити insight з API на рядок для БД."""
        actions = insight.get("actions") or []
        conversions = 0
        conversion_value = 0
        for a in actions:
            if a.get("action_type") in ("purchase", "omni_purchase", "lead", "complete_registration"):
                conversions += self._safe_int(a.get("value"))
            if a.get("action_type") == "purchase" and "value" in a:
                conversion_value += self._safe_float(a.get("value"))
        # value is in action_values for some action types
        action_values = insight.get("action_values") or []
        for av in action_values:
            if av.get("action_type") in ("purchase", "omni_purchase"):
                conversion_value += self._safe_float(av.get("value"))

        return {
            "date": insight.get("date_start", ""),
            "account_id": self.ad_account_id,
            "campaign_id": insight.get("campaign_id", ""),
            "campaign_name": insight.get("campaign_name", ""),
            "adset_id": insight.get("adset_id", ""),
            "adset_name": insight.get("adset_name", ""),
            "ad_id": insight.get("ad_id", ""),
            "ad_name": insight.get("ad_name", ""),
            "impressions": self._safe_int(insight.get("impressions")),
            "clicks": self._safe_int(insight.get("clicks")),
            "spend": self._safe_float(insight.get("spend")),
            "reach": self._safe_int(insight.get("reach")),
            "cpm": self._safe_float(insight.get("cpm")),
            "cpc": self._safe_float(insight.get("cpc")),
            "ctr": self._safe_float(insight.get("ctr")),
            "conversions": conversions,
            "conversion_value": conversion_value,
        }

    def fetch(self) -> list[dict]:
        if not FACEBOOK_AVAILABLE:
            raise ImportError("Встановіть: pip install facebook-business")

        FacebookAdsApi.init(access_token=self.access_token)
        account = AdAccount(f"act_{self.ad_account_id}")

        params = {
            "time_range": {
                "since": self.date_from.strftime("%Y-%m-%d"),
                "until": self.date_to.strftime("%Y-%m-%d"),
            },
            "time_increment": 1,  # по днях
            "fields": [
                "date_start", "campaign_id", "campaign_name",
                "adset_id", "adset_name", "ad_id", "ad_name",
                "impressions", "clicks", "spend", "reach",
                "cpm", "cpc", "ctr", "actions", "action_values",
            ],
        }

        insights = account.get_insights(params=params)
        fields = [
            "date_start", "campaign_id", "campaign_name",
            "adset_id", "adset_name", "ad_id", "ad_name",
            "impressions", "clicks", "spend", "reach",
            "cpm", "cpc", "ctr", "actions", "action_values",
        ]
        rows = []
        for insight in insights:
            d = {}
            for f in fields:
                try:
                    val = insight.get(f) if hasattr(insight, "get") else getattr(insight, f, None)
                    if val is not None:
                        d[f] = val
                except (KeyError, AttributeError):
                    pass
            rows.append(self._parse_insight(d))
        return rows
