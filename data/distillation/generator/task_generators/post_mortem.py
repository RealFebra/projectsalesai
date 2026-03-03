"""
post_mortem.py — POST_MORTEM Task Generator
=============================================
Kampanya sonrası analiz / post-mortem. (~%3)
"""

import random
from ..scenarios import build_scenario


_POSTMORTEM_CONTEXTS = [
    "Son {days} günlük kampanya sona erdi. Toplam harcama {spend}, hedef ROAS {target_roas}x, gerçekleşen {actual_roas}x. Ne iyi gitti, ne kötü?",
    "Flash sale kampanyası bitti: {hours}h sürdü, {spend} harcandı. Hedef CPA {target_cpa} idi, gerçekleşen {actual_cpa}. Learnings çıkar.",
    "A/B test tamamlandı: Variant A (broad) vs Variant B (interest). Hangisi kazandı ve neden? Sonraki adımlar?",
    "Seasonal kampanya (Black Friday/Bayram) post-mortem: YoY karşılaştırma + next year önerileri.",
    "Yeni pazarda ilk 30 gün tamamlandı. Benchmark vs gerçekleşen karşılaştırması, scale kararı.",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """POST_MORTEM örneği üret."""
    base = build_scenario(
        platform=platform,
        task_type="POST_MORTEM",
        example_id=example_id,
        **kwargs,
    )

    ctx = random.choice(_POSTMORTEM_CONTEXTS)
    ctx = ctx.replace("{days}", str(random.choice([7, 14, 30, 60, 90])))
    ctx = ctx.replace("{hours}", str(random.choice([24, 48, 72])))
    ctx = ctx.replace("{spend}", str(random.randint(500, 50000)))
    ctx = ctx.replace("{target_roas}", str(round(random.uniform(2.0, 6.0), 1)))
    ctx = ctx.replace("{actual_roas}", str(round(random.uniform(0.5, 4.0), 1)))
    ctx = ctx.replace("{target_cpa}", str(random.randint(10, 80)))
    ctx = ctx.replace("{actual_cpa}", str(random.randint(15, 120)))

    section = (
        f"\n\n### Post-Mortem Bağlamı\n"
        f"- {ctx}\n"
        f"- Beklenen çıktı: what worked, what didn't, root cause, actionable learnings, next steps.\n"
    )

    base["user"] = base["user"] + section
    base["tags"].append("post_mortem")

    return base
