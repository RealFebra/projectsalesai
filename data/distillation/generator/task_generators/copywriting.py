"""
copywriting.py — COPYWRITING Task Generator
=============================================
Reklam metni üretimi senaryoları. (Toplam dağılımın %25'i)
Ek alan: user promptuna copy-specific talimatlar ekler.
"""

import random
from ..scenarios import build_scenario, _pick_business_context
from .. import config as C
from .. import platforms as P
from .. import schemas as S


_COPY_ANGLES = [
    "problem_solution", "social_proof", "urgency_scarcity", "benefit_first",
    "curiosity_hook", "storytelling", "comparison", "authority",
    "before_after", "fear_of_missing_out", "emotional_appeal",
    "data_driven", "testimonial", "unboxing_experience", "lifestyle",
    "aspirational", "counter_intuitive", "question_hook", "direct_offer",
    "educational_value", "community_belonging", "transformation",
    "insider_secret", "seasonal_tie_in", "price_anchor",
]

_COPY_FORMATS = [
    "short_primary (125 char)", "long_primary (250+ char)", "headline (40 char)",
    "description (30 char)", "ugc_script", "video_overlay_text",
    "carousel_card_text", "story_text", "pin_description",
    "sponsored_post_native", "search_ad_copy (RSA)",
]

_TONES = [
    "confident_premium", "playful_casual", "urgent_direct", "empathetic_warm",
    "data_backed_authoritative", "witty_clever", "minimalist_clean",
    "luxury_aspirational", "friendly_conversational", "bold_disruptive",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """Tek bir COPYWRITING örneği üret — copy-specific ek talimatlar içerir."""
    base = build_scenario(
        platform=platform,
        task_type="COPYWRITING",
        example_id=example_id,
        **kwargs,
    )

    # Enrich the user prompt with copy-specific instructions
    num_copies = random.randint(3, 6)
    angles = random.sample(_COPY_ANGLES, min(num_copies, len(_COPY_ANGLES)))
    formats = random.sample(_COPY_FORMATS, min(random.randint(2, 4), len(_COPY_FORMATS)))
    tone = random.choice(_TONES)

    copy_brief = (
        f"\n\n### Copy Brief\n"
        f"- Üretilecek kopya sayısı: {num_copies}\n"
        f"- Hedeflenen angle'lar: {', '.join(angles)}\n"
        f"- Formatlar: {', '.join(formats)}\n"
        f"- Ton: {tone}\n"
        f"- Dil: Türkçe (uluslararası pazar ise İngilizce de kabul)\n"
        f"- JSON yanıtında \"ad_copies\" arrayı ekle: her copy için angle, primary, headline, cta, format, platform_tone_notes alanları olacak.\n"
        f"- Her copy 'ün CTA'sı farklı olsun.\n"
    )

    base["user"] = base["user"] + copy_brief
    if "copywriting" not in base["tags"]:
        base["tags"].append("copywriting_brief")

    return base
