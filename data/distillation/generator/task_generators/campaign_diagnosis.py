"""
campaign_diagnosis.py — CAMPAIGN_DIAGNOSIS Task Generator
===========================================================
Kampanya teşhis senaryoları üretir. (Toplam dağılımın %40'ı)
"""

from ..scenarios import build_scenario


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """Tek bir CAMPAIGN_DIAGNOSIS örneği üret."""
    return build_scenario(
        platform=platform,
        task_type="CAMPAIGN_DIAGNOSIS",
        example_id=example_id,
        **kwargs,
    )
