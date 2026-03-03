"""
multi_channel.py — MULTI_CHANNEL Task Generator
=================================================
Cross-channel orchestration: budget split, incrementality, overlap, dedup. (~%3)
"""

import random
from ..scenarios import build_scenario
from .. import platforms as P


_MULTI_CHANNEL_CONTEXTS = [
    "Meta + Google Ads birlikte çalışıyor. Toplam bütçe {budget} {currency}/ay. Optimal split nedir?",
    "Meta + TikTok + Google: 3 kanal çalışıyor ama toplam CPA artıyor. Cannibalization var mı?",
    "Retarget audiences overlap: Meta retarget ve Google retarget aynı kişilere ulaşıyor. Dedup stratejisi gerekli.",
    "Incrementality sorusu: Meta'yı kapatırsak bu conversions organik/Google'dan gelir miydi? Test planı oluştur.",
    "Budget reallocation: {budget} {currency} mevcut bütçeyi 3 kanal arasında yeniden dağıt (mevcut split suboptimal).",
    "Attribution conflicts: Meta 120 purchase, Google 95 purchase, backend 100 purchase. Double-counting %{overlap_pct}.",
    "New channel pilot: {new_channel} ekleniyor. Mevcut Meta + Google miksine nasıl entegre edilir?",
    "MER (Marketing Efficiency Ratio) düşüyor: toplam spend / toplam revenue oranı kötüleşiyor. Hangi kanal zarar veriyor?",
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """MULTI_CHANNEL örneği üret — her zaman 'mixed' platform."""
    # Multi-channel always uses 'mixed' platform
    platform = "mixed"

    base = build_scenario(
        platform=platform,
        task_type="MULTI_CHANNEL",
        example_id=example_id,
        **kwargs,
    )

    # Generate multi-channel context
    multi_ctx = P.generate_mixed_platform_context()

    ctx_template = random.choice(_MULTI_CHANNEL_CONTEXTS)
    ctx_template = ctx_template.replace("{budget}", str(random.randint(5000, 100000)))
    ctx_template = ctx_template.replace("{currency}", random.choice(["USD", "EUR", "TRY"]))
    ctx_template = ctx_template.replace("{overlap_pct}", str(random.randint(15, 45)))
    ctx_template = ctx_template.replace("{new_channel}", random.choice(["TikTok", "Pinterest", "Reddit", "Snapchat", "LinkedIn"]))

    # Channel metrics summary
    channel_lines = []
    for ch_plat, ch_data in multi_ctx["channels"].items():
        m = ch_data["metrics"]
        channel_lines.append(
            f"  - {P.get_platform_config(ch_plat)['display_name']}: "
            f"budget share %{ch_data['budget_share_pct']}, "
            f"spend={m['spend']}, ROAS={m['roas']}x, CPA={m['cpa']}, "
            f"purchases={m['purchases']}"
        )

    section = (
        f"\n\n### Multi-Channel Bağlam\n"
        f"- {ctx_template}\n"
        f"- Aktif kanallar: {', '.join(multi_ctx['platforms'])}\n"
        f"- Kanal bazlı metrikler:\n"
        + "\n".join(channel_lines) +
        f"\n- Beklenen çıktı: budget reallocation önerisi, incrementality assessment, dedup stratejisi, unified KPI framework.\n"
    )

    base["user"] = base["user"] + section
    base["platform"] = "mixed"
    base["tags"].append("multi_channel")
    base["tags"].extend(multi_ctx["platforms"])

    return base
