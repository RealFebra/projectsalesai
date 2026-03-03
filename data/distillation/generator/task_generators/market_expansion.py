"""
market_expansion.py — MARKET_EXPANSION Task Generator
=====================================================
Yeni pazar girişi stratejisi. (~%3 dağılıma dahil)
"""

import random
from ..scenarios import build_scenario


_EXPANSION_CONTEXTS = [
    "Yeni pazar: {market}. Mevcut pazarda ROAS {home_roas}x. Hedef: ilk 30 günde {target} purchase. Budget: {budget} {currency}/gün.",
    "{market} pazarına expansion planlı. Lokal competitor analysis: {competitors} aktif. Fiyat benchmark: {price_range}.",
    "Multi-market simultaneous launch: {markets}. Toplam bütçe {budget} {currency}. Market bazlı bütçe allokasyonu + creative localization gerekli.",
    "{market} pazarında test kampanyası 14 gün önce başladı. CPA {test_cpa} (hedef: {target_cpa}). Scale kararı verilecek.",
    "Mevcut en iyi pazar ({home_market}) saturated. Growth için {market} expansion mantıklı mı? Data-driven karar çerçevesi.",
]

_MARKETS = [
    "Almanya (DACH)", "İngiltere (UK)", "Fransa", "Suudi Arabistan (KSA)",
    "Birleşik Arap Emirlikleri (UAE)", "ABD (US)", "Japonya", "Güney Kore",
    "Brezilya", "Meksika", "Hindistan", "Endonezya", "Avustralya",
    "Polonya", "İspanya", "İtalya", "Hollanda", "İsveç",
]

_COMPETITORS = [
    "3 lokal marka + 2 global player",
    "5+ lokal competitor, fiyat savaşı aktif",
    "1 dominant player (%60 market share) + niş markalar",
    "Yeni pazar — henüz agresif competition yok",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """MARKET_EXPANSION örneği üret."""
    base = build_scenario(
        platform=platform,
        task_type="MARKET_EXPANSION",
        example_id=example_id,
        force_problem="new_market_cold_start",
        **kwargs,
    )

    ctx = random.choice(_EXPANSION_CONTEXTS)
    ctx = ctx.replace("{market}", random.choice(_MARKETS))
    ctx = ctx.replace("{markets}", ", ".join(random.sample(_MARKETS, 3)))
    ctx = ctx.replace("{home_roas}", str(round(random.uniform(2.0, 6.0), 1)))
    ctx = ctx.replace("{target}", str(random.randint(50, 500)))
    ctx = ctx.replace("{budget}", str(random.randint(100, 5000)))
    ctx = ctx.replace("{currency}", random.choice(["USD", "EUR", "TRY", "GBP"]))
    ctx = ctx.replace("{competitors}", random.choice(_COMPETITORS))
    ctx = ctx.replace("{price_range}", f"{random.randint(20, 80)}-{random.randint(100, 300)} EUR")
    ctx = ctx.replace("{test_cpa}", str(random.randint(15, 80)))
    ctx = ctx.replace("{target_cpa}", str(random.randint(10, 50)))
    ctx = ctx.replace("{home_market}", random.choice(["Türkiye", "ABD", "UK", "Almanya"]))

    section = (
        f"\n\n### Market Expansion Bağlamı\n"
        f"- {ctx}\n"
        f"- Beklenen çıktı: market entry strategy, budget plan, creative localization brief, KPI milestones, risk assessment.\n"
    )

    base["user"] = base["user"] + section
    base["tags"].append("market_expansion")

    return base
