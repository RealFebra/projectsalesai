"""
Fine-Tuning Script — Qwen3-VL-8B-Thinking (Streaming Mode)
============================================================
Unsloth ile QLoRA 4-bit fine-tuning.
Dataset'leri doğrudan HuggingFace'den streaming ile okur — disk alanı gerekmez.
GPU: NVIDIA RTX 5070 Ti (16GB VRAM)
"""

import os
import sys
import yaml
import argparse
import json
import tempfile
from pathlib import Path
from itertools import islice

# CRITICAL TEMP FIX: Bunlar hiçbir kütüphane yüklenmeden EN ÜSTTE olmalı
os.environ["HF_HOME"] = "E:\\projectfinetune\\models"
os.environ["TRANSFORMERS_CACHE"] = "E:\\projectfinetune\\models"
os.environ["HF_DATASETS_CACHE"] = "E:\\projectfinetune\\models\\datasets"
os.environ["XDG_CACHE_HOME"] = "E:\\projectfinetune\\models"

os.environ["TRITON_CACHE_DIR"] = "E:\\projectfinetune\\models\\tmp"
os.environ["TMPDIR"] = "E:\\projectfinetune\\models\\tmp"
os.environ["TEMP"] = "E:\\projectfinetune\\models\\tmp"
os.environ["TMP"] = "E:\\projectfinetune\\models\\tmp"

# Python'un kendi temp dizinini de zorla
tempfile.tempdir = "E:\\projectfinetune\\models\\tmp"

# ── Disable Triton/torch.compile BEFORE any library import ──────────────────
# Windows'ta C compiler yok, Triton JIT compilation tamamen kapatılmalı.
os.environ["UNSLOTH_COMPILE_MAXIMUM"] = "0"
os.environ["UNSLOTH_COMPILE_DEBUG"] = "0"
os.environ["UNSLOTH_DISABLE_CUSTOM_KERNELS"] = "1"
os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["TORCH_USE_TRITON"] = "0"
os.environ["TORCHINDUCTOR_DISABLE"] = "1"       # Inductor'i tamamen kapat
os.environ["TRITON_INTERPRET"] = "1"             # Triton'u interpreter moduna al (C compiler gerekmez)
os.environ["TORCH_INDUCTOR_DISABLE_CUDA_GRAPHS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# ─────────────────────────────────────────────────────────────────────────────

# CRITICAL: Yönlendirmelerden SONRA Unsloth yüklenmeli
from unsloth import FastVisionModel

# Windows terminal Unicode fix
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
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
# TIER 1 DATASETS — Doğrudan fine-tune materyali
# ============================================================
TIER1_DATASETS = [
    # Satış Konuşmaları & Instruction
    {"hf_id": "goendalf666/sales-conversations",             "type": "sales",           "max": None},
    {"hf_id": "goendalf666/sales-conversations-instruction-customer", "type": "instruction",     "max": None},
    {"hf_id": "goendalf666/sales-textbook_for_convincing_and_selling", "type": "textbook",      "max": None},
    {"hf_id": "DeepMostInnovations/saas-sales-conversations", "type": "sales",           "max": None},
    # gwenshap/sales-transcripts -> Parquet kolon uyumsuzlugu, atlandı

    # Müşteri Desteği & Çağrı Merkezi
    {"hf_id": "bitext/Bitext-customer-support-llm-chatbot-training-dataset", "type": "instruction",     "max": None},

    # İkna & Müzakere
    # stanfordnlp/craigslist_bargains -> HF script destegi kalktı, atlandı
    {"hf_id": "kchawla123/casino",                            "type": "negotiation",     "max": None},
    # mikelewis0/deal_or_no_dialog -> HF script destegi kalktı, atlandı
    {"hf_id": "spawn99/PersuasionForGood",                    "type": "persuasion",      "max": None, "kwargs": {"split": "FullDialog"}},
    {"hf_id": "Anthropic/persuasion",                         "type": "persuasion",      "max": None},

    # Reklam Kopyası & Programmatic Ads
    {"hf_id": "smangrul/ad-copy-generation",                  "type": "instruction",     "max": None},  # tek kolon 'content', Llama instruct format
    {"hf_id": "PeterBrendan/Ads_Creative_Ad_Copy_Programmatic","type": "adcopy",          "max": None},
    {"hf_id": "PeterBrendan/Ads_Creative_Text_Programmatic",  "type": "adcopy",          "max": None},
    {"hf_id": "cyberagent/AdTEC",                             "type": "adcopy",          "max": None},
    {"hf_id": "c-s-ale/Product-Descriptions-and-Ads",         "type": "adcopy",          "max": None},
    {"hf_id": "suolyer/copywriting",                          "type": "adcopy",          "max": None, "kwargs": {"split": "validation"}},

    # Sosyal Medya & Marketing
    {"hf_id": "RafaM97/marketing_social_media",               "type": "instruction",     "max": None},
    {"hf_id": "Yale-LILY/aeslc",                              "type": "instruction",     "max": None},

    # Ürün Açıklamaları
    {"hf_id": "philschmid/amazon-product-descriptions-vlm",   "type": "adcopy",          "max": None},

    # Sentiment ve Reviewler
    {"hf_id": "fancyzhx/amazon_polarity",                     "type": "sentiment",       "max": None},
    {"hf_id": "Yelp/yelp_review_full",                        "type": "sentiment",       "max": None},
    {"hf_id": "fancyzhx/yelp_polarity",                       "type": "sentiment",       "max": None},
    {"hf_id": "stanfordnlp/sst2",                             "type": "sentiment",       "max": None},
    {"hf_id": "mteb/imdb",                                    "type": "sentiment",       "max": None},
    {"hf_id": "mltrev23/financial-sentiment-analysis",        "type": "sentiment",       "max": None},
    {"hf_id": "Sp1786/multiclass-sentiment-analysis-dataset", "type": "sentiment",       "max": None},
    {"hf_id": "yuncongli/chat-sentiment-analysis",            "type": "sentiment",       "max": None},
]


# ============================================================
# CONVERTERS — Her dataset tipini Qwen3-VL chat formatına çevir
# ============================================================

def convert_sales(item) -> dict | None:
    """Satış konuşması → analiz formatı. (Dictionary ve Liste Keys uyumlu)"""
    text = ""
    if "0" in item and "1" in item:
        # Array gibi structure (satır = mesajlar serisi)
        messages = [str(item[k]) for k in sorted(item.keys(), key=lambda x: int(x) if x.isdigit() else 999) if item[k]]
        text = "\n".join(messages)
    else:
        text = item.get("conversation", item.get("text", item.get("content", "")))
        
    if not text or len(str(text)) < 50:
        return None
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Bu satış konuşmasını analiz et. Kullanılan satış tekniklerini ve iyileştirme önerilerini belirt:\n\n{str(text)[:3000]}"},
            {"role": "assistant", "content": f"<think>\nBu satış konuşmasını adım adım analiz edeyim.\n</think>\n\nBu konuşmada kullanılan satış tekniklerini inceliyorum:\n\n{str(text)[:2000]}"}
        ]
    }


def convert_instruction(item) -> dict | None:
    """Instruction/input/output formatı → chat format. (Email/VLM/Genel uyumlu)"""
    instruction, input_text, output = "", "", ""
    
    # Tek-kolon datasetler (sadece 'text', '0', veya 'content' key'i olan)
    if len(item) <= 2 and ("0" in item or "text" in item or "content" in item):
        raw_val = str(item.get("content", item.get("text", item.get("0", ""))))
        
        # Llama instruct format: <s>[INST] <<SYS>>...<</SYS>> ... [/INST] response </s>
        if "[/INST]" in raw_val:
            parts = raw_val.split("[/INST]", 1)
            instruction = parts[0].replace("<s>", "").replace("[INST]", "").replace("<<SYS>>", "").replace("<</SYS>>", "").strip()
            output = parts[1].replace("</s>", "").strip()
        elif "### Response:" in raw_val:
            parts = raw_val.split('### Response:')
            instruction = parts[0].replace('### Instruction:', '').strip()
            output = parts[1].strip()
        elif "Assistant:" in raw_val:
            parts = raw_val.split('Assistant:', 1)
            instruction = parts[0].replace('User:', '').strip()
            output = parts[1].strip()
        else:
            instruction = "Müşteri ile satış asistanı arasındaki bu metni analiz et ve değerlendir."
            output = raw_val
    else:
        # Email dataset desteği (Yale-LILY/aeslc)
        if "email_body" in item or "subject_line" in item:
            email = item.get("email_body", "")
            subject = item.get("subject_line", "")
            if email and subject:
                instruction = f"Bu email için kısa ve etkili bir konu başlığı yaz:\n\n{str(email)[:2000]}"
                output = str(subject)
            else:
                return None
        # VLM / görsel tabanlı dataset desteği
        elif "caption" in item or "image_description" in item:
            caption = item.get("caption", item.get("image_description", ""))
            product_name = item.get("product_name", item.get("title", ""))
            if caption:
                instruction = f"Bu ürün görseli için etkili bir ürün açıklaması yaz."
                if product_name:
                    instruction += f"\nÜrün: {str(product_name)}"
                output = str(caption)
            else:
                return None
        else:
            # Genel fallback
            instruction = item.get("instruction", item.get("question", item.get("text", "")))
            input_text = item.get("input", item.get("context", item.get("0", "")))
            output = item.get("output", item.get("response", item.get("answer", item.get("label", ""))))

    if output is None or (isinstance(output, str) and len(output.strip()) < 2):
        return None

    user_content = str(instruction)
    if input_text and str(input_text) != str(instruction):
        user_content += f"\n\n{str(input_text)}"

    if not user_content.strip():
        return None

    # Wrap output with <think> for Qwen3-VL Thinking format
    thinking = f"<think>\nInstruction'u anliyorum: {user_content[:200]}\nEn iyi yaniti olusturuyorum.\n</think>"
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content[:3000]},
            {"role": "assistant", "content": f"{thinking}\n\n{str(output)[:3000]}"}
        ]
    }


def convert_sentiment(item) -> dict | None:
    """Sentiment/Review dataseti → duygu analizi formatı. (text+label, sentence+sentiment, review+stars)"""
    # Metin bul (text, sentence, content, review, Sentence, tweet...)
    text_val = (item.get("text", "") or item.get("sentence", "") or item.get("Sentence", "")
                or item.get("content", "") or item.get("review", "") or item.get("tweet", "")
                or item.get("comment", ""))
    
    # Label bul (label, sentiment, Sentiment, label_text, stars...)
    label_val = item.get("label", item.get("sentiment", item.get("Sentiment",
                item.get("label_text", item.get("stars", item.get("rating", None))))))

    if not text_val or label_val is None:
        return None
    
    text_val = str(text_val)[:2500]
    label_str = str(label_val)
    
    # Sayısal labeli anlam kazandır
    SENTIMENT_MAP = {
        "0": "Negatif", "1": "Pozitif",  # Binary (amazon_polarity, yelp_polarity, imdb)
        "2": "Nötr", "3": "Pozitif", "4": "Çok Pozitif",  # 5-sınıflı (yelp_review_full)
    }
    readable = SENTIMENT_MAP.get(label_str, label_str)
    
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Bu metnin duygu analizini yap ve satış/pazarlama açısından değerlendir:\n\n{text_val}"},
            {"role": "assistant", "content": f"<think>\nBu metni duygu analizi perspektifinden inceliyorum.\n</think>\n\nDuygu Analizi Sonucu: {readable}\n\nBu metin {readable.lower()} bir ton taşıyor. Satış ve pazarlama açısından {'müşteri memnuniyeti yüksek, bu tür geri bildirimler pazarlama materyali olarak kullanılabilir' if readable in ['Pozitif', 'Çok Pozitif'] else 'iyileştirme gerektiren noktalar var, müşteri deneyimi stratejileri gözden geçirilmeli'}."}
        ]
    }


def convert_textbook(item) -> dict | None:
    """Textbook → Q&A formatı."""
    text = item.get("text", item.get("content", ""))
    if not text or len(str(text)) < 100:
        return None
    text = str(text)[:3000]
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Satış teknikleri hakkında şu konuyu açıkla:\n\n{text[:500]}"},
            {"role": "assistant", "content": f"<think>\nBu satış konseptini detaylı açıklayayım.\n</think>\n\n{text}"}
        ]
    }


def convert_persuasion(item) -> dict | None:
    """İkna / persuasion dataset'leri → analiz formatı. (PersuasionForGood 'Unit' kolonu dahil)"""
    claim = item.get("claim", "")
    argument = item.get("argument", item.get("text", item.get("dialogue", item.get("Unit", ""))))
    if not argument or len(str(argument)) < 20:
        return None

    if claim:
        return {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Bu iddia hakkında satış psikolojisi perspektifinden ikna edici bir argüman oluştur:\n\n{str(claim)}"},
                {"role": "assistant", "content": f"<think>\nBu iddia için en etkili ikna tekniklerini düşüneyim.\n</think>\n\n{str(argument)[:3000]}"}
            ]
        }
    else:
        return {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Bu ikna diyaloğundaki kullanılan stratejileri analiz et:\n\n{str(argument)[:2000]}"},
                {"role": "assistant", "content": f"<think>\nİkna stratejilerini tespit edeyim.\n</think>\n\nBu diyalogda şu ikna stratejileri kullanılmış:\n\n{str(argument)[:2000]}"}
            ]
        }


def convert_negotiation(item) -> dict | None:
    """Müzakere dataset'leri → analiz formatı."""
    dialogue = item.get("dialogue", item.get("utterance", item.get("text", "")))

    # Nested chat_logs desteği
    if not dialogue and "chat_logs" in item:
        logs = item["chat_logs"]
        if isinstance(logs, list):
            dialogue = "\n".join([f"{m.get('role','?')}: {m.get('text','')}"
                                  for m in logs if isinstance(m, dict)])

    if not dialogue or len(str(dialogue)) < 50:
        return None

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Bu müzakere diyaloğunu analiz et. Kullanılan taktikleri ve sonuçları değerlendir:\n\n{str(dialogue)[:3000]}"},
            {"role": "assistant", "content": f"<think>\nMüzakere taktiklerini ve dinamiklerini analiz edeyim.\n</think>\n\nBu müzakerede şu dinamikler var:\n\n{str(dialogue)[:2000]}"}
        ]
    }


def convert_adcopy(item) -> dict | None:
    """Reklam kopyası → oluşturma formatı. (Büyük/küçük harf + AdTEC + VLM uyumlu)"""
    # Ürün adını bul (onca farklı kolon ismi arasında — boşluklu key'ler dahil)
    product = (item.get("product_name", "") or item.get("Product", "") or item.get("Product Name", "")
               or item.get("name", "") or item.get("product", ""))
    desc = (item.get("product_description", "") or item.get("Description", "") or item.get("description", "")
            or item.get("About Product", "") or item.get("lp_text", "") or item.get("content", ""))
    ad = (item.get("ad_copy", "") or item.get("Ad", "") or item.get("ad", "") or item.get("ad_text", "")
          or item.get("text", "") or item.get("creative_text", "") or item.get("title", ""))

    # Eğer ad boş ama desc doluysa, desc'i ad olarak kullan (VLM/product-description datasetleri)
    if (not ad or len(str(ad)) < 10) and desc and len(str(desc)) >= 10:
        ad = desc
        desc = ""  # desc'i ad'a taşıdık, tekrar etmesin

    if not ad or len(str(ad)) < 10:
        return None

    user_msg = "Bu ürün için etkili bir reklam metni yaz. Satış psikolojisi tekniklerini kullan:\n\n"
    if product:
        user_msg += f"Ürün: {str(product)}\n"
    if desc:
        user_msg += f"Açıklama: {str(desc)[:500]}\n"

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": f"<think>\nBu ürün için dikkat çekici ve ikna edici bir reklam metni hazırlayayım.\n</think>\n\n{str(ad)[:2000]}"}
        ]
    }


CONVERTERS = {
    "sales": convert_sales,
    "instruction": convert_instruction,
    "textbook": convert_textbook,
    "persuasion": convert_persuasion,
    "negotiation": convert_negotiation,
    "adcopy": convert_adcopy,
    "sentiment": convert_sentiment,
}


# ============================================================
# STREAMING DATA LOADER
# ============================================================

def load_all_datasets_streaming(max_total: int = 100000) -> list[dict]:
    """
    Tüm Tier 1 dataset'leri streaming modunda yükler.
    Disk kullanmaz — doğrudan HuggingFace'den okur.
    """
    from datasets import load_dataset

    all_examples = []

    for ds_info in TIER1_DATASETS:
        hf_id = ds_info["hf_id"]
        ds_type = ds_info["type"]
        max_samples = ds_info["max"]
        converter = CONVERTERS.get(ds_type, convert_instruction)

        print(f"\n  📡 Streaming: {hf_id} (max {max_samples})")

        try:
            kwargs = ds_info.get("kwargs", {})
            split_name = kwargs.pop("split", "train")  # Bazı datasetler farkli split kullanir
            ds = load_dataset(hf_id, split=split_name, **kwargs)
            
            count = 0
            errors = 0
            for item in ds:
                if count >= max_samples:
                    break
                try:
                    example = converter(item)
                    if example:
                        all_examples.append(example)
                        count += 1
                except Exception:
                    errors += 1
                    if errors > 50:
                        break

            print(f"     ✅ {count} örnek alındı" + (f" ({errors} hata)" if errors else ""))

        except Exception as e:
            print(f"     ❌ Hata: {str(e)[:100]}")

        if len(all_examples) >= max_total:
            print(f"\n  ⚡ Max toplam ({max_total}) ulaşıldı, durduruluyor.")
            break

    print(f"\n  📊 TOPLAM (HF): {len(all_examples)} örnek toplandı")
    
    # ------ KAGGLE / EXTERNAL LOCAL DATA (OPSIYONEL) ------
    import os, json
    local_external_file = os.environ.get(
        "EXTERNAL_DATA_PATH",
        "D:/datasets/sales_marketing/external_training_data.jsonl"
    )
    if os.path.exists(local_external_file):
        print(f"\n  Yerel dis kaynak verisi yukleniyor... ({local_external_file})")
        local_count = 0
        try:
            with open(local_external_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        instruction = record.get("instruction", "")
                        input_txt   = record.get("input", "")
                        output_txt  = record.get("output", "")
                        user_msg    = instruction
                        if input_txt:
                            user_msg += f"\n\n{input_txt}"
                        think_block = f"<think>\nInstruction'u anliyorum: {user_msg[:150]}\nEn iyi yaniti olusturuyorum.\n</think>"
                        formatted = {
                            "messages": [
                                {"role": "system",    "content": SYSTEM_PROMPT},
                                {"role": "user",      "content": user_msg},
                                {"role": "assistant", "content": f"{think_block}\n\n{output_txt}"}
                            ]
                        }
                        all_examples.append(formatted)
                        local_count += 1
                    except json.JSONDecodeError:
                        continue
            print(f"     {local_count:,} adet yerel Kaggle/External kayit egitime eklendi.")
        except Exception as e:
            print(f"     Yerel veri okuma hatasi: {e}")
    else:
        print(f"\n  Yerel dis kaynak bulunamadi, atlanıyor: {local_external_file}")
        print("     H200 sunucusunda sadece HF datasetleriyle egitim yapilacak.")

    # ------ KAGGLE PRE-CONVERTED DATA (H200 setup scriptiyle indirilmis) ------
    kaggle_jsonl = os.environ.get(
        "KAGGLE_DATA_PATH",
        "/workspace/models/tmp/kaggle_data.jsonl"
    )
    if os.path.exists(kaggle_jsonl):
        print(f"\n  Kaggle pre-converted data yukleniyor: {kaggle_jsonl}")
        kg_count = 0
        with open(kaggle_jsonl, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec:
                        all_examples.append(rec)
                        kg_count += 1
                except json.JSONDecodeError:
                    continue
        print(f"     {kg_count:,} Kaggle metin ornegi eklendi.")

    # ------ TABULAR DATA (convert_tabular_datasets.py ciktisi) ------
    tabular_jsonl = os.environ.get(
        "TABULAR_DATA_PATH",
        "/workspace/models/tmp/tabular_data.jsonl"
    )
    if os.path.exists(tabular_jsonl):
        print(f"\n  Tablosal Kaggle data yukleniyor: {tabular_jsonl}")
        tab_count = 0
        with open(tabular_jsonl, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec:
                        all_examples.append(rec)
                        tab_count += 1
                except json.JSONDecodeError:
                    continue
        print(f"     {tab_count:,} tablosal ornek eklendi.")
    # ----------------------------------------------------------------

    print(f"\n  GENEL TOPLAM: {len(all_examples)} ornek egitime girecek.")
    # -------------------------------------------------------

    return all_examples


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Fine-tune Qwen3-VL-8B-Thinking (Streaming)")
    parser.add_argument("--config", type=str, default="./configs/finetune_config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Sadece 10 step (test)")
    parser.add_argument("--max-samples", type=int, default=9999999999, help="Max toplam örnek")
    parser.add_argument("--from-file", type=str, default=None,
                        help="Hazır JSONL dosyasından oku (streaming yerine)")
    args = parser.parse_args()

    # Config yükle
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("=" * 60)
    print("  🧠 Qwen3-VL-8B-Thinking — Fine-Tuning (Streaming)")
    print(f"  Model: {config['model']['name']}")
    print(f"  LoRA Rank: {config['lora']['r']} | Alpha: {config['lora']['lora_alpha']}")
    print(f"  Batch: {config['training']['per_device_train_batch_size']} × {config['training']['gradient_accumulation_steps']}")
    print(f"  Epochs: {config['training']['num_train_epochs']}")
    print(f"  Max Samples: {args.max_samples}")
    print(f"  HF Cache: {os.environ.get('HF_HOME', 'default')}")
    print("=" * 60)

    # ── 1. Model yükle ──
    print("\n📦 Model yükleniyor (4-bit quantized)...")

    model, tokenizer = FastVisionModel.from_pretrained(
        model_name=config["model"]["name"],
        max_seq_length=config["model"]["max_seq_length"],
        load_in_4bit=config["model"]["load_in_4bit"],
        dtype=None,
    )
    print("✅ Model yüklendi!")

    # ── 2. LoRA ekle ──
    print("\n🔧 LoRA adaptörleri ekleniyor...")
    model = FastVisionModel.get_peft_model(
        model,
        r=config["lora"]["r"],
        lora_alpha=config["lora"]["lora_alpha"],
        lora_dropout=config["lora"]["lora_dropout"],
        target_modules=config["lora"]["target_modules"],
        bias=config["lora"]["bias"],
        use_gradient_checkpointing=config["lora"]["use_gradient_checkpointing"],
    )

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"✅ LoRA eklendi! Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # ── 3. Veri yükle ──
    from datasets import load_dataset as hf_load_dataset
    
    train_file = args.from_file
    if not train_file or not os.path.exists(train_file):
        print(f"❌ HATA: Egitim dosyasi bulunamadi: {train_file}")
        print("Lütfen once download_all_raw_datasets.py ve filter_and_convert.py calistirin.")
        return

    print(f"\n� Dataset diskten yükleniyor: {train_file}")
    dataset = hf_load_dataset("json", data_files=train_file, split="train")

    if args.max_samples and args.max_samples < len(dataset):
        print(f"✂️  Dataset {args.max_samples} ornek ile sinirlandiriliyor...")
        dataset = dataset.select(range(args.max_samples))

    print(f"💬 Chat template uygulaniyor... ({len(dataset):,} ornek)")
    def format_chat(example):
        text = tokenizer.apply_chat_template(
            example["messages"], 
            tokenize=False, 
            add_generation_prompt=False
        )
        return {"text": text}

    dataset = dataset.map(format_chat, num_proc=os.cpu_count() or 4, desc="Applying chat template")

    print(f"✅ Dataset hazır: {len(dataset):,} örnek")

    # Train/eval split
    split = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = split["train"]
    eval_dataset = split["test"]
    print(f"   Train: {len(train_dataset)} | Eval: {len(eval_dataset)}")

    # ── 4. Eğitim ──
    print("\n🚀 Eğitim başlıyor...")
    from trl import SFTTrainer, SFTConfig

    tc = config["training"]

    if args.dry_run:
        tc["num_train_epochs"] = 1
        tc["max_steps"] = 10
        tc["logging_steps"] = 1
        tc["save_strategy"] = "no"
        print("⚡ DRY-RUN: sadece 10 step")

    sft_config = SFTConfig(
        output_dir=tc["output_dir"],
        num_train_epochs=tc["num_train_epochs"],
        per_device_train_batch_size=tc["per_device_train_batch_size"],
        gradient_accumulation_steps=tc["gradient_accumulation_steps"],
        learning_rate=tc["learning_rate"],
        lr_scheduler_type=tc["lr_scheduler_type"],
        warmup_ratio=tc["warmup_ratio"],
        weight_decay=tc["weight_decay"],
        bf16=tc["bf16"],
        logging_steps=tc["logging_steps"],
        save_strategy=tc["save_strategy"],
        save_total_limit=tc.get("save_total_limit", 3),
        seed=tc.get("seed", 42),
        max_grad_norm=tc.get("max_grad_norm", 1.0),
        optim=tc.get("optim", "adamw_8bit"),
        max_seq_length=config["model"]["max_seq_length"],
        dataset_text_field="text",
        max_steps=tc.get("max_steps", -1),
        report_to="none",
        torch_compile=False, # YENI: Windows compiler hatalarini önlemek için devre disi
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )

    # GPU durumu
    import torch
    if torch.cuda.is_available():
        gpu_stats = torch.cuda.get_device_properties(0)
        alloc = torch.cuda.memory_allocated() / 1024**3
        total_mem = gpu_stats.total_memory / 1024**3
        print(f"📊 GPU: {alloc:.1f} / {total_mem:.1f} GB kullanılıyor")

    stats = trainer.train()

    print(f"\n{'='*60}")
    print(f"  ✅ EĞİTİM TAMAMLANDI!")
    print(f"  Loss: {stats.training_loss:.4f}")
    print(f"  Steps: {stats.global_step}")
    print(f"{'='*60}")

    # ── 5. Kaydet ──
    if not args.dry_run:
        out = tc["output_dir"] + "/final"
        print(f"\n💾 Kaydediliyor: {out}")
        model.save_pretrained(out)
        tokenizer.save_pretrained(out)

        # GGUF (opsiyonel)
        try:
            model.save_pretrained_gguf(out + "-gguf", tokenizer, quantization_method="q4_k_m")
            print(f"✅ GGUF kaydedildi: {out}-gguf")
        except Exception as e:
            print(f"⚠️  GGUF opsiyonel, atlandı: {e}")

    print("\n🎉 Tamamlandı!")


if __name__ == "__main__":
    main()
