"""
anomaly_triage.py — ANOMALY_TRIAGE Task Generator
===================================================
Tracking anomaly, reporting delay, outage şüphesi senaryoları. (~%3)
"""

import random
from ..scenarios import build_scenario


_ANOMALY_TYPES = [
    {
        "type": "pixel_drop",
        "desc": "Pixel event'leri son {hours}h'de %{drop_pct} düştü. Purchase event: platform {p_val}, backend {b_val}.",
        "force_problem": "pixel_tracking_broken",
    },
    {
        "type": "capi_dedup_fail",
        "desc": "CAPI + Pixel dual setup ama dedup çalışmıyor. Conversion'lar 2x count ediliyor. EMQ: %{emq}.",
        "force_problem": "capi_event_dedup_issue",
    },
    {
        "type": "reporting_delay",
        "desc": "Son {hours}h verisi eksik/gecikmeli. Platform status page: '{status}'. Karar mekanizması bloke.",
        "force_problem": "reporting_delay_48h",
    },
    {
        "type": "platform_outage",
        "desc": "Bugün tüm account'larda spend %{drop_pct} düştü. API yanıt süresi {latency}ms (normal: 200ms). Outage?",
        "force_problem": "platform_outage_suspected",
    },
    {
        "type": "utm_broken",
        "desc": "GA'da son {days}d'de 'direct/none' trafik %{pct} arttı. UTM parametreleri {status}.",
        "force_problem": "utm_parameter_missing",
    },
    {
        "type": "attribution_mismatch",
        "desc": "Platform {p_conv} conversion raporluyor, GA {ga_conv}, CRM {crm_conv}. Fark: %{diff_pct}.",
        "force_problem": "attribution_mismatch",
    },
    {
        "type": "data_lag",
        "desc": "Son 3 günün datası güvenilir değil. Revenue normalizasyon süresi {hours}h. Erken optimizasyon riskli.",
        "force_problem": "data_lag_3_day",
    },
]


def generate(platform: str, example_id: str, **kwargs) -> dict:
    """ANOMALY_TRIAGE örneği üret — tracking/reporting anomaly senaryoları."""
    anomaly = random.choice(_ANOMALY_TYPES)

    desc = anomaly["desc"]
    desc = desc.replace("{hours}", str(random.choice([6, 12, 24, 48, 72])))
    desc = desc.replace("{drop_pct}", str(random.randint(30, 90)))
    desc = desc.replace("{p_val}", str(random.randint(5, 50)))
    desc = desc.replace("{b_val}", str(random.randint(10, 80)))
    desc = desc.replace("{emq}", str(random.randint(30, 75)))
    desc = desc.replace("{status}", random.choice(["All systems operational", "Investigating", "Partial outage", "Unknown"]))
    desc = desc.replace("{latency}", str(random.randint(800, 5000)))
    desc = desc.replace("{days}", str(random.choice([3, 7, 14])))
    desc = desc.replace("{pct}", str(random.randint(20, 60)))
    desc = desc.replace("{p_conv}", str(random.randint(20, 200)))
    desc = desc.replace("{ga_conv}", str(random.randint(10, 150)))
    desc = desc.replace("{crm_conv}", str(random.randint(15, 180)))
    desc = desc.replace("{diff_pct}", str(random.randint(15, 55)))

    base = build_scenario(
        platform=platform,
        task_type="ANOMALY_TRIAGE",
        example_id=example_id,
        force_problem=anomaly["force_problem"],
        force_flags={"outage": True},
        **kwargs,
    )

    section = (
        f"\n\n### Anomaly Detayları\n"
        f"- Anomaly tipi: {anomaly['type']}\n"
        f"- {desc}\n"
        f"- Beklenen çıktı: root cause analizi, immediate triage steps, verification checklist, risk assessment.\n"
        f"- Karar verirken data güvenilirliğini değerlendir — emin olana kadar agresif aksiyon alma.\n"
    )

    base["user"] = base["user"] + section
    base["tags"].append("anomaly_triage")
    base["tags"].append(anomaly["type"])

    return base
