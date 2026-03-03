# 🎯 Satış & Reklam AI — Fine-Tuning Pipeline

> **Model:** Qwen3-VL-8B-Thinking | **GPU:** RTX 5070 Ti (16GB) | **Yöntem:** QLoRA 4-bit (Unsloth)

## Hızlı Başlangıç

```bash
# 1. Bağımlılıkları kur
pip install -r requirements.txt

# 2. Test eğitimi (10 step — streaming, disk gerekmez)
python scripts/finetune.py --dry-run

# 3. Tam eğitim (streaming, ~20K örnek otomatik toplanır)
python scripts/finetune.py

# 4. Test et
python scripts/inference.py --mode interactive
```

> **Not:** Dataset'ler HuggingFace'den **streaming** ile okunur — büyük disk alanı gerekmez. Model cache'i `D:\hf_cache`'e kaydedilir.

## Proje Yapısı

```
e:\projectfinetune\
├── requirements.txt                  # Python bağımlılıkları
├── README.md
├── configs/
│   └── finetune_config.yaml          # Model, LoRA, eğitim ayarları
├── scripts/
│   ├── finetune.py                   # Tek script: stream + dönüştür + eğit
│   └── inference.py                  # Chat, görsel analiz, benchmark
└── output/
    └── satis-reklam-ai/final/        # Fine-tune edilmiş model
```

## Fine-Tune Akışı

```
HuggingFace (15 dataset)         finetune.py                        output/
  Streaming ile oku ───────►  Qwen3-VL chat formatına  ───────►  LoRA Adaptörler
  (disk kullanmaz)              çevir + eğit                     + GGUF export
```

## Kullanım

```bash
# İnteraktif sohbet
python scripts/inference.py --mode interactive

# Benchmark (5 hazır senaryo)
python scripts/inference.py --mode benchmark

# Görsel analiz (reklam görseli)
python scripts/inference.py --mode single --image reklam.jpg --query "Bu reklamı analiz et"
```

## Tier 1 Dataset'ler (Otomatik Yüklenir)

| Kategori | Dataset'ler | Max Örnek |
|----------|-------------|-----------|
| Satış Konuşmaları | sales-conversations, SaaS sales, textbook | ~13K |
| İkna & Müzakere | Anthropic persuasion, CraigslistBargains, CaSiNo | ~8K |
| Reklam Kopyası | Ad copy generation, programmatic ads, copywriting | ~7K |
| Müşteri Destek | Bitext customer support | ~3K |
