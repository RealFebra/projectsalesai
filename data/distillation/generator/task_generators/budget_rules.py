"""
budget_rules.py — BUDGET_RULES_AUTOMATION Task Generator
=========================================================
if/then budget + bidding otomasyon kuralları. (Toplam dağılımın %10'u)
Ek alan: rules_json.
"""

import random
from ..scenarios import build_scenario


_RULE_CONDITIONS = [
    ("CPA > target * 1.3", "spend >= min_daily * 0.5"),
    ("ROAS < target * 0.7", "spend >= 50"),
    ("CTR < 0.5%", "impressions >= 1000"),
    ("Frequency > 4.0", "reach >= audience_size * 0.5"),
    ("CPC > target * 1.5", "clicks >= 20"),
    ("CPM > benchmark * 1.5", "impressions >= 5000"),
    ("CVR < 0.3%", "clicks >= 100"),
    ("Spend > daily_budget * 0.8 by noon", "day_fraction >= 0.5"),
    ("ROAS > target * 1.5", "conversions >= 10"),
    ("No conversions in 48h", "spend >= 100"),
    ("Learning phase > 7 days", "events < target_events * 0.5"),
    ("Impression share < 20%", "budget_limited == true"),
]

_RULE_ACTIONS = [
    "reduce_budget_15pct", "reduce_budget_25pct", "pause_entity",
    "increase_budget_10pct", "increase_budget_20pct",
    "switch_to_cost_cap", "switch_to_manual_cpc",
    "lower_bid_15pct", "raise_bid_10pct",
    "duplicate_and_test", "creative_refresh_trigger",
    "audience_expansion", "add_negative_keywords",
    "notify_team_slack", "hold_and_observe_24h",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """BUDGET_RULES_AUTOMATION örneği üret — rules_json formatında otomasyonlar."""
    base = build_scenario(
        platform=platform,
        task_type="BUDGET_RULES_AUTOMATION",
        example_id=example_id,
        **kwargs,
    )

    num_rules = random.randint(3, 7)
    rule_examples = random.sample(_RULE_CONDITIONS, min(num_rules, len(_RULE_CONDITIONS)))

    rules_section = (
        f"\n\n### Otomasyon Kuralları Talebi\n"
        f"- Toplam kural sayısı: {num_rules}\n"
        f"- Örnek durumlar:\n"
    )
    for cond, safety in rule_examples:
        action = random.choice(_RULE_ACTIONS)
        rules_section += f"  - IF {cond} AND {safety} THEN {action}\n"

    rules_section += (
        f"- JSON yanıtında \"rules_json\" arrayı ekle: her kural için if, then, safety alanları olacak.\n"
        f"- Guardrail: aynı gün bütçe değişimi max %25. Birden fazla kural birleştiğinde toplam değişim de %25'i geçmemeli.\n"
        f"- Her kuralda cooldown_hours belirt (aynı kural aynı entity'ye tekrar uygulanma süresi).\n"
        f"- Fallback action ekle: tüm kurallar tetiklenirse ne yapılacak?\n"
    )

    base["user"] = base["user"] + rules_section
    if "budget_rules" not in base["tags"]:
        base["tags"].append("automation_rules")

    return base
