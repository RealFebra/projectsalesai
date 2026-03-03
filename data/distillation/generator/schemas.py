"""
schemas.py — Metric Coherence Engine + Unified Ads Schema
==========================================================
Tutarlı metrik setleri üretir: spend → impressions → clicks → conversions → revenue → ROAS
"""

import random
import math
from typing import Optional


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def generate_coherent_metrics(
    *,
    spend: Optional[float] = None,
    cpm_range: tuple[float, float] = (3.0, 35.0),
    ctr_range: tuple[float, float] = (0.4, 4.5),
    cvr_range: tuple[float, float] = (0.5, 8.0),
    aov_range: tuple[float, float] = (20.0, 300.0),
    days: int = 7,
    low_spend: bool = False,
    high_frequency: bool = False,
    poor_ctr: bool = False,
    high_cpa: bool = False,
    negative_margin: bool = False,
    margin_pct: float = 0.50,
) -> dict:
    """
    Birbirine bağımlı, tutarlı metrik seti üretir.

    Dependency chain:
      spend → impressions (via CPM)
      impressions → clicks (via CTR)
      clicks → add_to_cart (via micro-cvr)
      add_to_cart → purchases (via checkout-cvr)
      purchases × AOV → revenue
      revenue / spend → ROAS
      revenue × margin_pct - spend → profit_est
    """
    rng = random.random

    # ── Spend ──
    if spend is None:
        if low_spend:
            spend = round(random.uniform(2.0, 28.0), 2)
        else:
            spend = round(random.uniform(50.0, 25000.0), 2)

    # ── CPM ──
    cpm = random.uniform(*cpm_range)
    if poor_ctr:
        cpm = random.uniform(cpm_range[0], cpm_range[0] + (cpm_range[1] - cpm_range[0]) * 0.4)

    # ── Impressions ──
    impressions = max(1, int((spend / cpm) * 1000))

    # ── Reach / Frequency ──
    if high_frequency:
        frequency = round(random.uniform(4.5, 12.0), 2)
    else:
        frequency = round(random.uniform(1.1, 4.0), 2)
    reach = max(1, int(impressions / frequency))

    # ── CTR → Clicks ──
    if poor_ctr:
        ctr = round(random.uniform(0.15, 0.6), 2)
    else:
        ctr = round(random.uniform(*ctr_range), 2)
    clicks = max(0, int(impressions * ctr / 100))

    # ── CPC ──
    cpc = round(spend / max(clicks, 1), 2)

    # ── Conversion funnel ──
    if high_cpa:
        cvr = round(random.uniform(0.1, 0.8), 2)
    else:
        cvr = round(random.uniform(*cvr_range), 2)

    add_to_cart_rate = round(random.uniform(cvr * 1.5, cvr * 4.0), 2)
    add_to_cart = max(0, int(clicks * add_to_cart_rate / 100))

    initiate_checkout_rate = round(random.uniform(0.3, 0.7), 2)
    initiate_checkout = max(0, int(add_to_cart * initiate_checkout_rate))

    # purchases from CVR on clicks
    purchases = max(0, int(clicks * cvr / 100))
    if purchases > initiate_checkout:
        purchases = max(0, initiate_checkout - random.randint(0, max(1, initiate_checkout // 5)))

    # ── Revenue / AOV ──
    aov = round(random.uniform(*aov_range), 2)
    revenue = round(purchases * aov, 2)

    # ── ROAS ──
    roas = round(revenue / max(spend, 0.01), 2)

    # ── CPA ──
    cpa = round(spend / max(purchases, 1), 2)

    # ── Profit ──
    cogs = revenue * (1 - margin_pct)
    profit_est = round(revenue * margin_pct - spend, 2)
    if negative_margin:
        # Force it negative even if ROAS looks decent
        margin_pct = round(random.uniform(0.08, 0.25), 2)
        profit_est = round(revenue * margin_pct - spend, 2)
        if profit_est >= 0:
            profit_est = round(-random.uniform(spend * 0.05, spend * 0.40), 2)

    return {
        "spend": spend,
        "impressions": impressions,
        "reach": reach,
        "frequency": frequency,
        "clicks": clicks,
        "ctr": ctr,
        "cpc": cpc,
        "cpm": round(cpm, 2),
        "add_to_cart": add_to_cart,
        "initiate_checkout": initiate_checkout,
        "purchases": purchases,
        "revenue": revenue,
        "aov": aov,
        "cvr": cvr,
        "cpa": cpa,
        "roas": roas,
        "margin_pct": round(margin_pct * 100, 1),
        "profit_est": profit_est,
        "days": days,
    }


def generate_video_metrics() -> dict:
    """Video-specific metrikleri üretir."""
    thumbstop_rate = round(random.uniform(8.0, 55.0), 1)
    vtr = round(random.uniform(5.0, 45.0), 1)  # % who watched 75%+
    view_rate = round(random.uniform(15.0, 65.0), 1)  # % who watched 3s+
    avg_watch_time = round(random.uniform(1.5, 22.0), 1)
    return {
        "thumbstop_rate": thumbstop_rate,
        "vtr": vtr,
        "view_rate": view_rate,
        "avg_watch_time_sec": avg_watch_time,
    }


def generate_search_metrics() -> dict:
    """Search/keyword-specific metrikleri üretir."""
    impression_share = round(random.uniform(5.0, 85.0), 1)
    top_impression_share = round(random.uniform(2.0, min(impression_share, 60.0)), 1)
    abs_top_impression_share = round(random.uniform(1.0, min(top_impression_share, 40.0)), 1)
    quality_score = random.randint(1, 10)
    return {
        "impression_share": impression_share,
        "top_impression_share": top_impression_share,
        "abs_top_impression_share": abs_top_impression_share,
        "quality_score": quality_score,
    }


def generate_shopping_metrics() -> dict:
    """Shopping/feed-specific metrikleri üretir."""
    total_products = random.randint(50, 5000)
    active_products = int(total_products * random.uniform(0.60, 0.98))
    disapproved = total_products - active_products
    feed_health_pct = round(active_products / total_products * 100, 1)
    return {
        "total_products": total_products,
        "active_products": active_products,
        "disapproved_products": disapproved,
        "feed_health_pct": feed_health_pct,
    }


def generate_time_series(
    base_metrics: dict,
    windows: list[int] | None = None,
    trend: str = "declining",   # declining | improving | stable | volatile
) -> dict[str, dict]:
    """
    Birden fazla zaman penceresi için metrik snapshot üretir.
    trend parametresi metriklerin nasıl değiştiğini kontrol eder.
    """
    if windows is None:
        windows = [3, 7, 14]

    results = {}
    for w in sorted(windows, reverse=True):
        factor = 1.0
        if trend == "declining":
            # Daha eski = daha iyi → bugün kötü
            factor = 1.0 + (w - min(windows)) * random.uniform(0.02, 0.08)
        elif trend == "improving":
            factor = 1.0 - (w - min(windows)) * random.uniform(0.01, 0.05)
        elif trend == "volatile":
            factor = 1.0 + random.uniform(-0.15, 0.15)
        # else stable → factor = 1.0

        scaled = {}
        for k, v in base_metrics.items():
            if isinstance(v, (int, float)) and k not in ("days", "margin_pct"):
                scaled[k] = round(v * factor * (w / base_metrics.get("days", 7)), 2)
                if isinstance(v, int):
                    scaled[k] = max(0, int(scaled[k]))
            else:
                scaled[k] = v
        scaled["days"] = w
        # Recalculate derived metrics
        if scaled.get("clicks", 0) > 0 and scaled.get("impressions", 0) > 0:
            scaled["ctr"] = round(scaled["clicks"] / scaled["impressions"] * 100, 2)
        if scaled.get("clicks", 0) > 0 and scaled.get("spend", 0) > 0:
            scaled["cpc"] = round(scaled["spend"] / max(scaled["clicks"], 1), 2)
        if scaled.get("spend", 0) > 0 and scaled.get("impressions", 0) > 0:
            scaled["cpm"] = round(scaled["spend"] / max(scaled["impressions"], 1) * 1000, 2)
        if scaled.get("spend", 0) > 0:
            scaled["roas"] = round(scaled.get("revenue", 0) / max(scaled["spend"], 0.01), 2)
            scaled["cpa"] = round(scaled["spend"] / max(scaled.get("purchases", 1), 1), 2)

        results[f"last_{w}d"] = scaled

    return results


def build_entity_ref(
    platform: str,
    level: str = "campaign",
    name: str = "",
) -> str:
    """Platform-aware entity reference string üretir."""
    level_map = {
        "meta":       {"campaign": "Campaign", "adgroup": "AdSet",    "ad": "Ad"},
        "google_ads": {"campaign": "Campaign", "adgroup": "AdGroup",  "ad": "Ad", "keyword": "KW", "product_group": "ProductGroup", "asset_group": "AssetGroup"},
        "tiktok":     {"campaign": "Campaign", "adgroup": "AdGroup",  "ad": "Ad"},
        "x":          {"campaign": "Campaign", "adgroup": "AdGroup",  "ad": "Ad"},
        "linkedin":   {"campaign": "CampaignGroup", "adgroup": "Campaign", "ad": "Ad"},
        "pinterest":  {"campaign": "Campaign", "adgroup": "AdGroup",  "ad": "Pin"},
        "snap":       {"campaign": "Campaign", "adgroup": "AdSquad",  "ad": "Ad"},
        "reddit":     {"campaign": "Campaign", "adgroup": "AdGroup",  "ad": "Ad"},
        "amazon_ads": {"campaign": "Campaign", "adgroup": "AdGroup",  "ad": "Ad", "product_group": "ProductGroup"},
        "mixed":      {"campaign": "Campaign", "adgroup": "AdSet/AdGroup", "ad": "Ad"},
    }
    prefix = level_map.get(platform, {}).get(level, level.capitalize())
    return f"{prefix}:{name}" if name else prefix
