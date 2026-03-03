"""
Data Preparation — Qwen3-VL-8B-Thinking Fine-Tuning
====================================================
Ham dataset'leri Qwen3-VL chat formatına çevirir.
Text-only ve multimodal (image+text) örnekleri destekler.
"""

import os
import json
import random
import argparse
from pathlib import Path
from typing import Optional

# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """Sen bir satış psikolojisi ve dijital reklam stratejisi uzmanısın.
Türkiye ve global pazarları iyi bilirsin. Görevin:

1. Reklam kampanya verilerini analiz edip performans değerlendirmesi yapmak
2. Satış psikolojisi ve ikna tekniklerine dayalı stratejik öneriler sunmak
3. Meta Ads ve Google Ads optimizasyon tavsiyeleri vermek
4. Reklam görsellerini ve metinlerini analiz edip iyileştirme önerileri sunmak
5. Somut, uygulanabilir aksiyon planları oluşturmak

Her zaman somut rakamlar, sektörel benchmarklar ve psikolojik çerçeveler kullan.
Jenerik tavsiyelerden kaçın. Adım adım düşün ve muhakeme yap."""


# ============================================================
# FORMAT CONVERTERS — Her dataset tipi için ayrı converter
# ============================================================

def convert_sales_conversations(raw_path: Path) -> list[dict]:
    """goendalf666/sales-conversations formatını çevir."""
    examples = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            # Format: conversation text between customer and salesman
            text = item.get("conversation", item.get("text", ""))
            if not text:
                continue

            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "Bu satış konuşmasını analiz et. Satıcının kullandığı ikna tekniklerini, güçlü ve zayıf yönlerini belirle, ve iyileştirme önerileri sun:\n\n" + text},
                    {"role": "assistant", "content": "<think>\nBu satış konuşmasını adım adım analiz edeyim.\n</think>\n\n" + _generate_conversation_analysis(text)}
                ]
            })
    return examples


def convert_sales_instructions(raw_path: Path) -> list[dict]:
    """goendalf666/sales-conversations-instruction-customer formatını çevir."""
    examples = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            instruction = item.get("instruction", "")
            input_text = item.get("input", "")
            output_text = item.get("output", "")

            if not output_text:
                continue

            user_content = instruction
            if input_text:
                user_content += f"\n\n{input_text}"

            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": output_text}
                ]
            })
    return examples


def convert_persuasion_dataset(raw_path: Path) -> list[dict]:
    """Anthropic/persuasion ve PersuasionForGood formatlarını çevir."""
    examples = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            # Anthropic persuasion format
            if "claim" in item and "argument" in item:
                examples.append({
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Bu iddia hakkında ikna edici bir argüman oluştur. Satış psikolojisi tekniklerini kullan:\n\nİddia: {item['claim']}"},
                        {"role": "assistant", "content": f"<think>\nBu iddia için en etkili ikna tekniklerini düşüneyim.\n</think>\n\n{item['argument']}"}
                    ]
                })

            # PersuasionForGood format
            elif "dialogue" in item or "text" in item:
                text = item.get("dialogue", item.get("text", ""))
                if text:
                    examples.append({
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"Bu ikna diyaloğunu analiz et. Kullanılan ikna stratejilerini tespit et:\n\n{text}"},
                            {"role": "assistant", "content": _generate_persuasion_analysis(text)}
                        ]
                    })
    return examples


def convert_ad_copy(raw_path: Path) -> list[dict]:
    """smangrul/ad-copy-generation ve benzer formatları çevir."""
    examples = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            # Ad copy generation format
            product_name = item.get("product_name", item.get("name", ""))
            product_desc = item.get("product_description", item.get("description", ""))
            ad_text = item.get("ad_copy", item.get("ad_text", item.get("text", "")))

            if not ad_text:
                continue

            user_content = "Bu ürün için etkili bir reklam metni yaz. Satış psikolojisi tekniklerini kullan:\n\n"
            if product_name:
                user_content += f"Ürün: {product_name}\n"
            if product_desc:
                user_content += f"Açıklama: {product_desc}\n"

            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": f"<think>\nBu ürün için en etkili reklam stratejisini düşüneyim.\n</think>\n\n{ad_text}"}
                ]
            })
    return examples


def convert_negotiation(raw_path: Path) -> list[dict]:
    """CraigslistBargains, CaSiNo, Deal or No Deal formatlarını çevir."""
    examples = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            dialogue = item.get("dialogue", item.get("utterance", item.get("text", "")))
            if not dialogue:
                # Try nested formats
                if "chat_logs" in item:
                    dialogue = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('text', '')}"
                                         for msg in item["chat_logs"] if isinstance(msg, dict)])

            if not dialogue or len(str(dialogue)) < 50:
                continue

            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Bu müzakere diyaloğunu analiz et. Kullanılan müzakere taktiklerini, güçlü hamleleri ve geliştirilecek noktaları belirle:\n\n{dialogue}"},
                    {"role": "assistant", "content": _generate_negotiation_analysis(str(dialogue))}
                ]
            })
    return examples


def convert_generic(raw_path: Path) -> list[dict]:
    """Genel format: instruction/input/output veya text alanı olan dataset'ler."""
    examples = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            # instruction/input/output format
            if "instruction" in item:
                user_content = item["instruction"]
                if item.get("input"):
                    user_content += f"\n\n{item['input']}"
                output = item.get("output", "")
                if output:
                    examples.append({
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_content},
                            {"role": "assistant", "content": output}
                        ]
                    })

            # messages format (already in chat format)
            elif "messages" in item:
                msgs = item["messages"]
                if isinstance(msgs, list) and len(msgs) >= 2:
                    # Inject system prompt if missing
                    if msgs[0].get("role") != "system":
                        msgs.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
                    examples.append({"messages": msgs})

            # Simple text format
            elif "text" in item:
                text = item["text"]
                if len(text) > 100:
                    examples.append({
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"Bu metni satış ve pazarlama açısından analiz et:\n\n{text[:2000]}"},
                            {"role": "assistant", "content": f"Bu metni analiz ediyorum:\n\n{text[:2000]}"}
                        ]
                    })
    return examples


# ============================================================
# ANALYSIS GENERATORS — Placeholder analysis templates
# ============================================================

def _generate_conversation_analysis(text: str) -> str:
    """Satış konuşması analizi üret (placeholder — gerçek eğitimde GPT-4 ile zenginleştir)."""
    return f"""## Satış Konuşması Analizi

**Genel Değerlendirme:** Bu konuşmada satıcı müşteriyle etkileşime geçiyor.

**Tespit Edilen İkna Teknikleri:**
- Rapport Building (İlişki Kurma): Konuşmanın açılışında kullanılmış
- Active Listening (Aktif Dinleme): Müşteri ihtiyaçlarını anlamak için sorular sorulmuş

**İyileştirme Önerileri:**
1. Daha güçlü bir hook (dikkat çekici açılış) kullanılabilir
2. Social proof (sosyal kanıt) eklenmeli
3. Urgency (aciliyet) hissi oluşturulmalı
4. Closing tekniği daha net olmalı"""


def _generate_persuasion_analysis(text: str) -> str:
    """İkna diyaloğu analizi üret."""
    return f"""## İkna Stratejisi Analizi

**Kullanılan Teknikler:**
- Reciprocity (Karşılıklılık): Küçük bir jeste karşı büyük bir istek
- Social Proof (Sosyal Kanıt): Başkalarının da aynı şeyi yaptığı vurgusu
- Authority (Otorite): Uzman görüşüne referans

**Etkinlik Değerlendirmesi:** Orta-Yüksek
**Öneriler:** Scarcity (kıtlık) ve loss aversion (kayıptan kaçınma) teknikleri eklenerek etkinlik artırılabilir."""


def _generate_negotiation_analysis(text: str) -> str:
    """Müzakere analizi üret."""
    return f"""## Müzakere Analizi

**Kullanılan Taktikler:**
- Anchoring (Çapalama): İlk teklifle referans noktası belirleme
- BATNA Kullanımı: Alternatif seçeneklere referans
- Concession Strategy: Kademeli taviz verme

**Güçlü Yönler:**
1. İlk teklif stratejik olarak belirlenmiş
2. Karşı tarafın ihtiyaçları dinlenmiş

**Geliştirilecek Noktalar:**
1. Win-win çerçevesi daha güçlü kurulabilir
2. Değer bazlı müzakere tekniği uygulanabilir"""


# ============================================================
# DATASET → CONVERTER MAPPING
# ============================================================
CONVERTERS = {
    "sales_conversations": convert_sales_conversations,
    "sales_instructions": convert_sales_instructions,
    "sales_textbook": convert_generic,
    "saas_sales": convert_sales_conversations,
    "persuasion_for_good": convert_persuasion_dataset,
    "anthropic_persuasion": convert_persuasion_dataset,
    "craigslist_bargains": convert_negotiation,
    "casino_negotiation": convert_negotiation,
    "deal_or_no_deal": convert_negotiation,
    "ad_copy_generation": convert_ad_copy,
    "programmatic_ad_copy": convert_ad_copy,
    "programmatic_ad_text": convert_ad_copy,
    "copywriting": convert_generic,
    "ad_image_net": convert_generic,
    "amazon_product_vlm": convert_generic,
    # Tier 2
    "propaganda_detection": convert_generic,
    "marketing_social_media": convert_generic,
    "product_descriptions_ads": convert_ad_copy,
    "amazon_product_desc": convert_generic,
    "bitext_customer_support": convert_generic,
}


# ============================================================
# MAIN
# ============================================================

def process_all(raw_dir: Path, output_dir: Path, eval_split: float = 0.1):
    """Tüm raw dataset'leri işle, train/eval split yap."""
    output_dir.mkdir(parents=True, exist_ok=True)

    all_examples = []

    for raw_file in sorted(raw_dir.glob("*.jsonl")):
        name = raw_file.stem
        converter = CONVERTERS.get(name, convert_generic)

        print(f"  🔄 İşleniyor: {name}")
        try:
            examples = converter(raw_file)
            print(f"     ✅ {len(examples)} örnek çıkarıldı")
            all_examples.extend(examples)
        except Exception as e:
            print(f"     ❌ Hata: {e}")

    # Karıştır
    random.seed(42)
    random.shuffle(all_examples)

    # Split
    split_idx = int(len(all_examples) * (1 - eval_split))
    train_data = all_examples[:split_idx]
    eval_data = all_examples[split_idx:]

    # Kaydet
    train_file = output_dir / "train.jsonl"
    eval_file = output_dir / "eval.jsonl"

    with open(train_file, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(eval_file, "w", encoding="utf-8") as f:
        for item in eval_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"  VERİ HAZIRLIK TAMAMLANDI")
    print(f"  Toplam: {len(all_examples)} örnek")
    print(f"  Train:  {len(train_data)} → {train_file}")
    print(f"  Eval:   {len(eval_data)} → {eval_file}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Veri Hazırlama")
    parser.add_argument("--raw-dir", type=str, default="./data/raw",
                        help="Ham veri dizini")
    parser.add_argument("--output-dir", type=str, default="./data/processed",
                        help="İşlenmiş veri dizini")
    parser.add_argument("--eval-split", type=float, default=0.1,
                        help="Evaluation split oranı")
    args = parser.parse_args()

    process_all(Path(args.raw_dir), Path(args.output_dir), args.eval_split)


if __name__ == "__main__":
    main()
