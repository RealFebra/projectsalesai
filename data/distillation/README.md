# Omni-Platform Ads Distillation — 1M Dataset Generator

## Amaç
TÜM reklam platformlarında çalışabilecek distillation-ready prompt arşivi.
Teacher model sadece JSON döndürür; student model SFT + DPO ile eğitilir.

## Desteklenen Platformlar
`meta` | `google_ads` | `tiktok` | `x` | `linkedin` | `pinterest` | `snap` | `reddit` | `amazon_ads` | `mixed`

## Task Families (10)
`CAMPAIGN_DIAGNOSIS` (40%) | `COPYWRITING` (25%) | `CREATIVE_BRIEF` (10%) | `BUDGET_RULES_AUTOMATION` (10%) | `STRATEGY_PLAYBOOK` | `POST_MORTEM` | `LANDING_OFFER` | `ANOMALY_TRIAGE` | `MULTI_CHANNEL` | `MARKET_EXPANSION`

## Guardrails
- Aynı gün bütçe değişimi max %25
- Spend < 30 → ölçüm/deney öner, agresif karar verme
- Learning phase reset etme
- Marj negatifse ROAS iyi olsa bile kâr odaklı aksiyon

## Kullanım

```bash
# Tam 1M üret (50K'lık batch'ler halinde):
cd e:\projectfinetune\data\distillation
python -m generator.run --total 1000000 --batch-size 50000

# Küçük test:
python -m generator.run --total 100 --batch-size 100

# DPO pairs + Eval set:
python -m generator.dpo_generator --output-dir .
python -m generator.eval_generator --output-dir .

# Doğrulama:
python -m generator.validate --dir .
```

## Çıktı Dosyaları
| Dosya | İçerik |
|-------|--------|
| `dataset.jsonl` | 1M prompt (merged) |
| `dataset_batch_XXXX.jsonl` | Batch dosyaları |
| `dpo_pairs.jsonl` | Pair üretim talimatları + 2 örnek |
| `eval_set.jsonl` | 30 edge-case senaryo |
