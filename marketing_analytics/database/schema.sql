-- Marketing Analytics SQLite Schema
-- Уніфікована схема для зберігання даних з різних рекламних платформ

-- ============================================
-- FACEBOOK / META ADS
-- ============================================
CREATE TABLE IF NOT EXISTS facebook_ads_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    account_id TEXT,
    campaign_id TEXT,
    campaign_name TEXT,
    adset_id TEXT,
    adset_name TEXT,
    ad_id TEXT,
    ad_name TEXT,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend REAL DEFAULT 0,
    reach INTEGER DEFAULT 0,
    cpm REAL,
    cpc REAL,
    ctr REAL,
    conversions INTEGER DEFAULT 0,
    conversion_value REAL DEFAULT 0,
    raw_data TEXT,  -- JSON для додаткових полів
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, campaign_id, adset_id, ad_id)
);

CREATE INDEX IF NOT EXISTS idx_facebook_date ON facebook_ads_daily(date);
CREATE INDEX IF NOT EXISTS idx_facebook_campaign ON facebook_ads_daily(campaign_id);

-- ============================================
-- GOOGLE ADS
-- ============================================
CREATE TABLE IF NOT EXISTS google_ads_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    customer_id TEXT,
    campaign_id TEXT,
    campaign_name TEXT,
    ad_group_id TEXT,
    ad_group_name TEXT,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    cost REAL DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_value REAL DEFAULT 0,
    ctr REAL,
    avg_cpc REAL,
    avg_cpm REAL,
    raw_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, campaign_id, ad_group_id)
);

CREATE INDEX IF NOT EXISTS idx_google_date ON google_ads_daily(date);
CREATE INDEX IF NOT EXISTS idx_google_campaign ON google_ads_daily(campaign_id);

-- ============================================
-- TIKTOK ADS
-- ============================================
CREATE TABLE IF NOT EXISTS tiktok_ads_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    advertiser_id TEXT,
    campaign_id TEXT,
    campaign_name TEXT,
    adgroup_id TEXT,
    adgroup_name TEXT,
    ad_id TEXT,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend REAL DEFAULT 0,
    reach INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_value REAL DEFAULT 0,
    cpm REAL,
    cpc REAL,
    ctr REAL,
    raw_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, campaign_id, adgroup_id, ad_id)
);

CREATE INDEX IF NOT EXISTS idx_tiktok_date ON tiktok_ads_daily(date);
CREATE INDEX IF NOT EXISTS idx_tiktok_campaign ON tiktok_ads_daily(campaign_id);

-- ============================================
-- VIEW: Об'єднана аналітика (всі платформи)
-- ============================================
CREATE VIEW IF NOT EXISTS marketing_unified_daily AS
SELECT 
    date,
    'facebook' AS platform,
    campaign_id,
    campaign_name,
    impressions,
    clicks,
    spend AS cost,
    conversions,
    conversion_value,
    ctr,
    cpc
FROM facebook_ads_daily
UNION ALL
SELECT 
    date,
    'google' AS platform,
    campaign_id,
    campaign_name,
    impressions,
    clicks,
    cost,
    conversions,
    conversion_value,
    ctr,
    avg_cpc AS cpc
FROM google_ads_daily
UNION ALL
SELECT 
    date,
    'tiktok' AS platform,
    campaign_id,
    campaign_name,
    impressions,
    clicks,
    spend AS cost,
    conversions,
    conversion_value,
    ctr,
    cpc
FROM tiktok_ads_daily;

-- ============================================
-- VIEW: Щоденні агрегати по платформах
-- ============================================
CREATE VIEW IF NOT EXISTS platform_daily_totals AS
SELECT 
    date,
    platform,
    SUM(impressions) AS total_impressions,
    SUM(clicks) AS total_clicks,
    SUM(cost) AS total_spend,
    SUM(conversions) AS total_conversions,
    SUM(conversion_value) AS total_conversion_value
FROM marketing_unified_daily
GROUP BY date, platform;
