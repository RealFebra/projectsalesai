"""
dpo_generator.py — DPO Pair Üretici
=====================================
Chosen (guardrail-compliant) vs Rejected (aggressive/reckless) pair örnekleri üretir.

Kullanım:
    python -m generator.dpo_generator --output-dir ./
"""

import json
import random
import argparse
from pathlib import Path

# ──────────────────────────────────────────────
# DPO PAIR INSTRUCTIONS (header)
# ──────────────────────────────────────────────

DPO_INSTRUCTIONS = {
    "description": "DPO Pair Generation Instructions for Omni-Platform Ads Distillation",
    "purpose": "SFT + DPO eğitimi için chosen/rejected pair üretimi. Her pair aynı user promptuna 2 farklı yanıt içerir.",
    "chosen_criteria": [
        "Guardrail'lara tam uyum (max %25 bütçe değişimi, low-spend koruması vb.)",
        "Somut entity_ref + change + reason + expected_impact",
        "Kanıt/metrik bazlı aksiyon önerileri",
        "Learning phase koruması",
        "Negatif marjda kâr odaklı düşünme",
        "Deney/ölçüm önerileri (özellikle low spend durumunda)",
    ],
    "rejected_criteria": [
        "Guardrail ihlali: %50+ bütçe değişimi, agresif scale, learning reset",
        "Kanıtsız/genel tavsiyeler ('daha iyi creative yap' gibi)",
        "Low spend'de agresif karar verme",
        "ROAS'a bakıp marjı görmezden gelme",
        "Boş motivasyon cümleleri içeren yanıtlar",
        "Platform-generic yanıtlar (platforma özgü detay yok)",
    ],
    "pair_generation_rules": [
        "Her pair aynı user prompt'u kullanır",
        "Chosen yanıt JSON şemasına tam uyar",
        "Rejected yanıt en az 2 guardrail ihlali içerir",
        "Rejected yanıtta en az 1 entity_ref eksik veya jenerik olmalı",
        "Her batch'te farklı problem tipleri ve platformlar kullanılmalı",
    ],
}


# ──────────────────────────────────────────────
# MINI EXAMPLES
# ──────────────────────────────────────────────

EXAMPLE_1_PROMPT = (
    "## CAMPAIGN_DIAGNOSIS — Meta Ads\n\n"
    "### İş Bağlamı\n- Sektör: fashion\n- Ürün: Organic Cotton T-Shirt\n"
    "- Fiyat: 45 EUR\n- Marj: %55\n- Ülke: Germany (DE)\n\n"
    "### Metrikler (son 7 gün)\n- Spend: 18.50 EUR\n- Purchases: 0\n"
    "- CTR: %0.42\n- ROAS: 0x\n\n"
    "### Sorun\nSon 7 günde spend < 30 ve conversion yok.\n\n"
    "### Guardrails\n- ⚠️ LOW SPEND: agresif karar verme, ölçüm/deney öner"
)

EXAMPLE_1_CHOSEN = {
    "id": "DPO-CHOSEN-001",
    "platform": "meta",
    "task_type": "CAMPAIGN_DIAGNOSIS",
    "summary": "Low spend durumu — yeterli data yok, karar vermek için deney gerekli.",
    "diagnosis": [
        "Spend 18.50 EUR ile ölçüm eşiğinin altında. 0 purchase ile istatistiksel anlam yok.",
        "CTR %0.42 düşük ama sample size yetersiz (low impression).",
        "Learning phase devam ediyor — reset etmek mantıksız.",
    ],
    "actions": [
        {
            "priority": "P1",
            "scope": "campaign",
            "action": "new_test",
            "entity_ref": "Campaign:Prospecting_DE",
            "change": "Günlük bütçeyi 15 EUR'a çıkar (mevcut ~2.6 EUR/gün) — daha hızlı data topla",
            "reason": "Mevcut spend ile karar vermek imkânsız. Min 50 EUR spend gerekli.",
            "guardrail": "Low spend guardrail: agresif scale yok, sadece ölçüm yeterli seviyeye getir",
            "expected_impact": "7 gün sonra yeterli data ile gerçek CPA/ROAS değerlendirmesi yapılabilir",
        }
    ],
    "experiments": [
        {
            "hypothesis": "Yüksek günlük bütçe ile 50+ impression/gün alınırsa CTR performansı netleşir.",
            "test": "Daily budget 15 EUR'a çıkar, 7 gün bekle.",
            "metric": "CTR + CPA",
            "success_threshold": "CTR > %1.0 ve en az 2 purchase",
            "duration_days": 7,
        }
    ],
    "risks": ["Hâlâ 0 conversion gelirse creative/audience sorunu var demektir."],
    "questions_to_ask": ["Organik trafik DE pazarından geliyor mu?", "Rakip fiyat aralığı nedir?"],
}

EXAMPLE_1_REJECTED = {
    "id": "DPO-REJECTED-001",
    "platform": "meta",
    "task_type": "CAMPAIGN_DIAGNOSIS",
    "summary": "Kampanya çalışmıyor, kapat ve yeniden başla.",
    "diagnosis": ["ROAS 0 — kampanya başarısız."],
    "actions": [
        {
            "priority": "P0",
            "scope": "campaign",
            "action": "pause",
            "entity_ref": "Campaign",
            "change": "Kampanyayı durdur, bütçeyi 3x artır (50 EUR/gün), yeni audience + creative ile başla",
            "reason": "0 conversion demek kampanya kötü demek.",
            "guardrail": "",
            "expected_impact": "Yeni setup ile daha iyi sonuçlar bekleniyor",
        }
    ],
    "experiments": [],
    "risks": [],
    "questions_to_ask": [],
}


EXAMPLE_2_PROMPT = (
    "## CAMPAIGN_DIAGNOSIS — Google Ads\n\n"
    "### İş Bağlamı\n- Sektör: electronics\n- Ürün: Wireless Headphones\n"
    "- Fiyat: 120 USD\n- Marj: %18\n- Ülke: US\n\n"
    "### Metrikler (son 14 gün)\n- Spend: 4200 USD\n- Revenue: 8400 USD\n"
    "- ROAS: 2.0x\n- Purchases: 70\n- Margin: %18\n- Profit_est: -2688 USD\n\n"
    "### Sorun\nROAS 2.0x ile hedefin üstünde ama marj %18 ile kâr negatif.\n\n"
    "### Guardrails\n- ⚠️ MARJ NEGATİF: ROAS iyi görünse bile kâr odaklı aksiyon üret"
)

EXAMPLE_2_CHOSEN = {
    "id": "DPO-CHOSEN-002",
    "platform": "google_ads",
    "task_type": "CAMPAIGN_DIAGNOSIS",
    "summary": "ROAS 2.0x ama %18 marj ile kâr negatif (-2688 USD). Kâr odaklı optimizasyona geçiş gerekli.",
    "diagnosis": [
        "Brüt ROAS 2.0x ama net marj %18 -> COGS dahil breakeven ROAS = 1/0.18 = 5.5x. Yani 5.5x altındaki her ROAS zararlı.",
        "14 günde -2688 USD zarar. Campaign profitable değil.",
        "CPA = 60 USD. Max CPA (profitability sınırı) = 120 × 0.18 = 21.6 USD. CPA 2.8x fazla.",
    ],
    "actions": [
        {
            "priority": "P0",
            "scope": "campaign",
            "action": "bidding_change",
            "entity_ref": "Campaign:Non-Brand_Search",
            "change": "Target ROAS'ı mevcut seviyeden 5.5x'e çıkar (breakeven) + %25 bütçe azalt",
            "reason": "Mevcut 2.0x ROAS ile her satış zarar üretiyor. Breakeven ROAS 5.5x.",
            "guardrail": "Max %25 budget cut (guardrail). Target ROAS artışı ile volume düşecek ama profitable volume elde edilecek.",
            "expected_impact": "Short-term: %50-70 volume düşüşü. Medium-term: profitability pozitife döner.",
        },
        {
            "priority": "P1",
            "scope": "keyword",
            "action": "pause",
            "entity_ref": "KW:ROAS < 3x olan generic keyword'ler",
            "change": "ROAS < 3x olan non-brand keyword'leri pauze et",
            "reason": "Generic keyword'ler muhtemelen en düşük ROAS'a sahip.",
            "guardrail": "Brand keyword'lere dokunma — defensive amaçlı.",
            "expected_impact": "Blended ROAS artışı, spend düşüşü, profit improvement.",
        }
    ],
    "experiments": [
        {
            "hypothesis": "Target ROAS 5.5x ile profitable volume elde edilebilir.",
            "test": "tROAS 5.5x set et, 7 gün bekle.",
            "metric": "Profit",
            "success_threshold": "Net profit > 0",
            "duration_days": 7,
        }
    ],
    "risks": ["Volume çok düşerse revenue hedefleri tutmayabilir — ama zarar etmekten iyidir."],
    "questions_to_ask": ["Marjı artırma imkânı var mı (fiyat artışı/COGS düşüşü)?"],
}

EXAMPLE_2_REJECTED = {
    "id": "DPO-REJECTED-002",
    "platform": "google_ads",
    "task_type": "CAMPAIGN_DIAGNOSIS",
    "summary": "ROAS 2.0x gayet iyi, bütçeyi artırarak scale edelim!",
    "diagnosis": ["ROAS pozitif, kampanya iyi çalışıyor."],
    "actions": [
        {
            "priority": "P0",
            "scope": "campaign",
            "action": "scale",
            "entity_ref": "Campaign",
            "change": "Bütçeyi %50 artır, daha fazla conversion al",
            "reason": "ROAS 2.0x ile kampanya kârlı, scale edersek daha çok kazanırız.",
            "guardrail": "",
            "expected_impact": "Daha fazla revenue!",
        }
    ],
    "experiments": [],
    "risks": [],
    "questions_to_ask": [],
}


def generate_dpo_file(output_dir: Path):
    """DPO pairs dosyasını üret."""
    output_file = output_dir / "dpo_pairs.jsonl"

    with open(output_file, "w", encoding="utf-8") as f:
        # Line 1: Instructions
        f.write(json.dumps(DPO_INSTRUCTIONS, ensure_ascii=False) + "\n")

        # Line 2: Example pair 1
        pair1 = {
            "pair_id": "DPO-PAIR-001",
            "user_prompt": EXAMPLE_1_PROMPT,
            "chosen": EXAMPLE_1_CHOSEN,
            "rejected": EXAMPLE_1_REJECTED,
            "rejection_reasons": [
                "GUARDRAIL_VIOLATION: entity_ref jenerik ('Campaign' — hangi campaign?)",
                "GUARDRAIL_VIOLATION: 3x bütçe artışı önerisi (max %25 kuralı ihlal)",
                "LOW_SPEND_VIOLATION: spend < 30 durumunda agresif karar (kapat + yeniden aç)",
                "KANITSIZ: '0 conversion = kötü kampanya' — sample size yetersiz",
                "EKSİK: deney planı yok, risk analizi yok, soru yok",
                "LEARNING_PHASE_RESET: kampanyayı kapatıp açmak learning'i sıfırlar",
            ],
        }
        f.write(json.dumps(pair1, ensure_ascii=False) + "\n")

        # Line 3: Example pair 2
        pair2 = {
            "pair_id": "DPO-PAIR-002",
            "user_prompt": EXAMPLE_2_PROMPT,
            "chosen": EXAMPLE_2_CHOSEN,
            "rejected": EXAMPLE_2_REJECTED,
            "rejection_reasons": [
                "MARGIN_BLIND: ROAS pozitif ama marj negatif — bunu görmezden geliyor",
                "GUARDRAIL_VIOLATION: %50 bütçe artışı (max %25 kuralı ihlal)",
                "YÜZEYSEL_DIAGNOSIS: 'ROAS pozitif = iyi' — breakeven ROAS hesaplanmamış",
                "KANITSIZ: 'daha fazla revenue!' — net profit negatif olduğunu atlıyor",
                "EKSİK: keyword-level analiz yok, experiment yok, risk yok",
            ],
        }
        f.write(json.dumps(pair2, ensure_ascii=False) + "\n")

    print(f"DPO pairs -> {output_file} (3 lines: instructions + 2 pairs)")
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=".")
    args = parser.parse_args()
    generate_dpo_file(Path(args.output_dir))
