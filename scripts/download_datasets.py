"""
Tier 1 Dataset Downloader — Satış & Reklam AI Fine-Tuning
=========================================================
Öncelikli dataset'leri Hugging Face'den indirir.
Tier 1: Doğrudan fine-tuning materyali (satış konuşmaları, ikna, reklam kopyası)
"""

import os
import json
import argparse
from pathlib import Path

# pip install datasets tqdm
from datasets import load_dataset
from tqdm import tqdm


# ============================================================
# TIER 1 — Doğrudan Fine-Tuning Materyali
# ============================================================
TIER1_DATASETS = {
    # -- Satış Konuşmaları --
    "sales_conversations": {
        "hf_id": "goendalf666/sales-conversations",
        "description": "3,410 synthetic sales conversations (GPT-3.5-turbo)",
        "priority": 1,
    },
    "sales_instructions": {
        "hf_id": "goendalf666/sales-conversations-instruction-customer",
        "description": "20,900 instruction-formatted sales conversation examples",
        "priority": 1,
    },
    "sales_textbook": {
        "hf_id": "goendalf666/sales-textbook_for_convincing_and_selling",
        "description": "Sales textbook: rapport, objection handling, closing",
        "priority": 1,
    },
    "saas_sales": {
        "hf_id": "DeepMostInnovations/saas-sales-conversations",
        "description": "SaaS sales dialogues with outcomes (GPT-4 generated)",
        "priority": 1,
    },
    # -- İkna & Müzakere --
    "persuasion_for_good": {
        "hf_id": "spawn99/PersuasionForGood",
        "description": "1,017 persuasion dialogues with strategy annotations",
        "priority": 1,
    },
    "anthropic_persuasion": {
        "hf_id": "Anthropic/persuasion",
        "description": "~3,940 persuasive arguments with effectiveness scores",
        "priority": 1,
    },
    "craigslist_bargains": {
        "hf_id": "stanfordnlp/craigslist_bargains",
        "description": "6,682 negotiation dialogues with persuasion techniques",
        "priority": 1,
    },
    "casino_negotiation": {
        "hf_id": "kchawla123/casino",
        "description": "1,030 negotiation dialogues with strategy annotations",
        "priority": 1,
    },
    "deal_or_no_deal": {
        "hf_id": "mikelewis0/deal_or_no_dialog",
        "description": "5,808 negotiation dialogues",
        "priority": 1,
    },
    # -- Reklam Kopyası --
    "ad_copy_generation": {
        "hf_id": "smangrul/ad-copy-generation",
        "description": "~1,140 instruction-tuned ad copy examples",
        "priority": 1,
    },
    "programmatic_ad_copy": {
        "hf_id": "PeterBrendan/Ads_Creative_Ad_Copy_Programmatic",
        "description": "7,097 real-world programmatic ad copy samples",
        "priority": 1,
    },
    "programmatic_ad_text": {
        "hf_id": "PeterBrendan/Ads_Creative_Text_Programmatic",
        "description": "Programmatic ad creative text",
        "priority": 1,
    },
    "copywriting": {
        "hf_id": "suolyer/copywriting",
        "description": "Copywriting dataset for marketing text generation",
        "priority": 1,
    },
    # -- Reklam Görselleri (VL modeli için) --
    "ad_image_net": {
        "hf_id": "PeterBrendan/AdImageNet",
        "description": "9,003 online ad creatives with extracted text and images",
        "priority": 1,
    },
    "amazon_product_vlm": {
        "hf_id": "philschmid/amazon-product-descriptions-vlm",
        "description": "Amazon product images + marketing descriptions (VLM ready)",
        "priority": 1,
    },
}

# ============================================================
# TIER 2 — Bilgi Zenginleştirme
# ============================================================
TIER2_DATASETS = {
    "propaganda_detection": {
        "hf_id": "SemEvalWorkshop/sem_eval_2020_task_11",
        "description": "18 persuasion/propaganda techniques with annotations",
        "priority": 2,
    },
    "marketing_social_media": {
        "hf_id": "RafaM97/marketing_social_media",
        "description": "689 marketing content generation examples",
        "priority": 2,
    },
    "product_descriptions_ads": {
        "hf_id": "c-s-ale/Product-Descriptions-and-Ads",
        "description": "100 clothing product descriptions with ads",
        "priority": 2,
    },
    "amazon_product_desc": {
        "hf_id": "Ateeqq/Amazon-Product-Description",
        "description": "421K Amazon product descriptions",
        "priority": 2,
    },
    "clickbait": {
        "hf_id": None,  # GitHub dataset, manual download
        "description": "32,000 clickbait vs non-clickbait headlines",
        "priority": 2,
        "url": "https://github.com/bhargaviparanjape/clickbait",
    },
    "bitext_customer_support": {
        "hf_id": "bitext/Bitext-customer-support-llm-chatbot-training-dataset",
        "description": "27,000+ customer service Q&A pairs",
        "priority": 2,
    },
}


def download_dataset(name: str, config: dict, output_dir: Path, max_samples: int = None):
    """Tek bir dataset'i indir ve JSONL olarak kaydet."""
    hf_id = config.get("hf_id")
    if not hf_id:
        print(f"  ⚠️  [{name}] Hugging Face ID yok, atlaniyor (manual download gerekli)")
        return None

    output_file = output_dir / f"{name}.jsonl"
    if output_file.exists():
        print(f"  ✅ [{name}] Zaten mevcut, atlaniyor")
        return output_file

    try:
        print(f"  ⬇️  [{name}] İndiriliyor: {hf_id}")
        ds = load_dataset(hf_id, trust_remote_code=True)

        # İlk split'i al (genelde train)
        split_name = list(ds.keys())[0]
        data = ds[split_name]

        if max_samples and len(data) > max_samples:
            data = data.select(range(max_samples))

        # JSONL olarak kaydet
        with open(output_file, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        print(f"  ✅ [{name}] {len(data)} örnek kaydedildi → {output_file}")
        return output_file

    except Exception as e:
        print(f"  ❌ [{name}] Hata: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Dataset Downloader")
    parser.add_argument("--tier", type=int, default=1, choices=[1, 2],
                        help="İndirilecek tier (1=Temel, 2=Zenginleştirme)")
    parser.add_argument("--output-dir", type=str, default="./data/raw",
                        help="İndirme dizini")
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Her dataset'ten max örnek sayısı (test için)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    datasets = TIER1_DATASETS if args.tier == 1 else {**TIER1_DATASETS, **TIER2_DATASETS}

    print(f"\n{'='*60}")
    print(f"  Satış & Reklam AI — Dataset İndirici")
    print(f"  Tier: {args.tier} | Toplam dataset: {len(datasets)}")
    print(f"  Çıktı dizini: {output_dir}")
    print(f"{'='*60}\n")

    results = {"success": [], "failed": [], "skipped": []}

    for name, config in datasets.items():
        result = download_dataset(name, config, output_dir, args.max_samples)
        if result:
            results["success"].append(name)
        elif config.get("hf_id") is None:
            results["skipped"].append(name)
        else:
            results["failed"].append(name)

    print(f"\n{'='*60}")
    print(f"  SONUÇ")
    print(f"  ✅ Başarılı: {len(results['success'])}")
    print(f"  ❌ Başarısız: {len(results['failed'])}")
    print(f"  ⚠️  Atlanan: {len(results['skipped'])}")
    print(f"{'='*60}\n")

    if results["failed"]:
        print("Başarısız dataset'ler:")
        for name in results["failed"]:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
