"""
strategy_playbook.py — STRATEGY_PLAYBOOK Task Generator
========================================================
Stratejik planlama ve playbook üretimi. (~%3)
"""

import random
from ..scenarios import build_scenario


_STRATEGY_CONTEXTS = [
    "Q4 Black Friday / holiday season yaklaşıyor. 3 aylık kampanya stratejisi oluştur.",
    "Yeni ürün lansmanı: 0 historical data. Launch-to-scale playbook oluştur.",
    "Rakip agresif fiyat kırdı. Defensive + offensive strateji öner.",
    "Mevcut müşteri LTV artırmak için retention + upsell stratejisi gerekli.",
    "CAC:LTV oranı kötüleşiyor. Unit economics düzeltme stratejisi oluştur.",
    "Organik + paid sinerji playbook'u: brand search + organic ranking + paid push dengesi.",
    "Yıllık bütçe planlaması: {budget_total} {currency} bütçe ile 12 aylık kanal dağılımı öner.",
    "Market maturity shift: growth → profitability geçişi için strateji güncellemesi.",
    "Multi-market rollout: 3 yeni ülkeye aynı anda giriş stratejisi.",
    "Influencer + paid media entegrasyonu: bütçe split, ölçüm, KPI framework.",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """STRATEGY_PLAYBOOK örneği üret."""
    base = build_scenario(
        platform=platform,
        task_type="STRATEGY_PLAYBOOK",
        example_id=example_id,
        **kwargs,
    )

    strategy_ctx = random.choice(_STRATEGY_CONTEXTS)
    strategy_ctx = strategy_ctx.replace("{budget_total}", str(random.randint(50000, 500000)))
    strategy_ctx = strategy_ctx.replace("{currency}", random.choice(["USD", "EUR", "TRY", "GBP"]))

    strategy_section = (
        f"\n\n### Strateji Bağlamı\n"
        f"- {strategy_ctx}\n"
        f"- Zaman ufku: {random.choice(['30 gün', '90 gün', '6 ay', '12 ay'])}\n"
        f"- Beklenen çıktı: phase-by-phase aksiyon planı, KPI hedefleri, risk senaryoları.\n"
        f"- JSON yanıtında actions arrayında her phase bir action olarak temsil edilsin.\n"
    )

    base["user"] = base["user"] + strategy_section
    base["tags"].append("strategy")

    return base
