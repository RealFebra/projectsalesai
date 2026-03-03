# Prompt Library — Omni-Platform Ads Distillation

## Task Type × Platform Matrix

Her hücre: hangi JSON alanlarını üretir + özel notlar.

| Task Type | Core Alanlar | Ek Alanlar | Platforms | Not |
|-----------|-------------|------------|-----------|-----|
| CAMPAIGN_DIAGNOSIS | summary, diagnosis, actions, experiments, risks | — | Tümü | %40 — ana görev tipi |
| COPYWRITING | summary, diagnosis, actions | `ad_copies[]`: angle, primary, headline, cta, format, platform_tone_notes | Tümü | %25 — copy brief eklenir |
| CREATIVE_BRIEF | summary, diagnosis, actions | `video_script[]`: sec, visual, voice, on_screen_text, edit_notes | meta, tiktok, snap, pinterest, x | %10 — video/UGC script |
| BUDGET_RULES_AUTOMATION | summary, diagnosis, actions | `rules_json[]`: if, then, safety, cooldown_hours | Tümü | %10 — if/then otomasyon |
| STRATEGY_PLAYBOOK | summary, diagnosis, actions, experiments | — | Tümü | ~%3 — uzun vadeli strateji |
| POST_MORTEM | summary, diagnosis, actions | — | Tümü | ~%3 — retrospective analiz |
| LANDING_OFFER | summary, diagnosis, actions | — | Tümü | ~%3 — landing + offer |
| ANOMALY_TRIAGE | summary, diagnosis, actions | — | Tümü | ~%3 — tracking/outage |
| MULTI_CHANNEL | summary, diagnosis, actions | Kanal bazlı metrikler | mixed (zorunlu) | ~%3 — cross-channel |
| MARKET_EXPANSION | summary, diagnosis, actions, experiments | — | Tümü | ~%3 — yeni pazar |

## Platform-Specific Özel Alanlar

| Platform | Senaryo Öğeleri | Özel Metrikler |
|----------|----------------|----------------|
| meta | adset_structure, creative_status, learning_info | frequency, learning_events |
| google_ads | campaign_structure, keyword_snapshot, quality_info | impression_share, quality_score |
| tiktok | creative_velocity, hook_analysis | thumbstop_rate, vtr |
| x | — | engagement vs conversion gap |
| linkedin | audience_targeting, lead_gen_info | CPL, form fill rate |
| pinterest | pin_metrics | save_rate, closeup_rate |
| snap | snap_metrics | swipe_up_rate, story_completion |
| reddit | reddit_context | comment_upvote_ratio |
| amazon_ads | catalog_status, acos_info | ACOS, TACOS, buy_box_pct |
| mixed | multi-channel context + per-channel metrics | MER, overlap_pct |

## Special Scenario Flags

| Flag | Oran | Tetiklenme |
|------|------|------------|
| `low_spend_guardrail` | %15 | spend < 30 (son 3 gün) |
| `negative_margin` | %10 | marj negatif, ROAS pozitif |
| `misleading_correlation` | %20 | gerçek sorun checkout/stok/fiyat |
| `outage_delay` | %10 | platform outage / data lag |

## JSONL Satır Formatı

```json
{
  "id": "PA-000001",
  "platform": "meta",
  "task_type": "CAMPAIGN_DIAGNOSIS",
  "language": "tr",
  "system": "(teacher system prompt: sadece JSON + guardrails)",
  "user": "(senaryo: iş bağlamı + metrikler + breakdown + sorun + istenen çıktı)",
  "schema_hint": "(şema hatırlatması)",
  "tags": ["CAMPAIGN_DIAGNOSIS", "meta", "fashion", "DE", "high_cpa_low_conversions"]
}
```
