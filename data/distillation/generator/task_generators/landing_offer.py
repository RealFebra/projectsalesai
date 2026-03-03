"""
landing_offer.py — LANDING_OFFER Task Generator
=================================================
Landing page ve offer optimizasyonu senaryoları. (~%3)
"""

import random
from ..scenarios import build_scenario


_LANDING_ISSUES = [
    "Bounce rate %{bounce} — mobile'da %{mobile_bounce}. Sayfa yükleme süresi {load_time}s.",
    "CTA yukarıda ama conversion düşük. Scroll depth: %{scroll_depth} kullanıcıları CTA'yı görüyor.",
    "A/B test: Variant A (video hero) vs B (static image). Variant A +{cvr_lift}% CVR ama bounce +{bounce_lift}%.",
    "Offer mismatch: reklamda %{ad_discount} indirim vaat ediliyor ama landing page'de %{actual_discount}.",
    "Multi-step form: step 1 → step 2 dropout %{dropout}. Form simplification gerekli mi?",
    "Price anchor eksik: ürün fiyatı tek başına gösteriliyor in karşılaştırma yok.",
    "Trust signal eksik: testimonial, review, güvenlik badge'i yok.",
    "Mobile UX: CTA button thumb zone dışında, font küçük, yatay scroll var.",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """LANDING_OFFER örneği üret."""
    base = build_scenario(
        platform=platform,
        task_type="LANDING_OFFER",
        example_id=example_id,
        **kwargs,
    )

    issue = random.choice(_LANDING_ISSUES)
    issue = issue.replace("{bounce}", str(random.randint(55, 90)))
    issue = issue.replace("{mobile_bounce}", str(random.randint(65, 95)))
    issue = issue.replace("{load_time}", str(round(random.uniform(2.0, 8.0), 1)))
    issue = issue.replace("{scroll_depth}", str(random.randint(20, 60)))
    issue = issue.replace("{cvr_lift}", str(random.randint(5, 25)))
    issue = issue.replace("{bounce_lift}", str(random.randint(3, 15)))
    issue = issue.replace("{ad_discount}", str(random.randint(20, 50)))
    issue = issue.replace("{actual_discount}", str(random.randint(5, 15)))
    issue = issue.replace("{dropout}", str(random.randint(40, 75)))

    section = (
        f"\n\n### Landing Page / Offer Detayları\n"
        f"- {issue}\n"
        f"- Mevcut landing page hız skoru (mobile): {random.randint(20, 70)}/100\n"
        f"- Beklenen çıktı: landing page iyileştirme önerileri + offer optimization + CTA testi planı.\n"
    )

    base["user"] = base["user"] + section
    base["tags"].append("landing_offer")

    return base
