"""
eval_generator.py — 30 Edge-Case Evaluation Set
=================================================
Sabit zor senaryolar — model kalitesini ölçmek için.

Kullanım:
    python -m generator.eval_generator --output-dir ./
"""

import json
import argparse
from pathlib import Path

from generator import config as C


# ──────────────────────────────────────────────
# 30 HARD EDGE-CASE SCENARIOS
# ──────────────────────────────────────────────

EVAL_SCENARIOS = [
    # 1-5: Low spend guardrail
    {
        "id": "EVAL-001", "platform": "meta", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Spend 8 EUR last 3d, 0 conversions. Client wants to kill campaign.",
        "edge_case": "low_spend_guardrail — must not make aggressive decisions",
        "expected_behavior": "Recommend observation/testing, NOT kill campaign",
    },
    {
        "id": "EVAL-002", "platform": "tiktok", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "TikTok campaign 2 days old, spend $12, thumbstop 45% but 0 purchases. Client panicking.",
        "edge_case": "low_spend + good early signal — patience needed",
        "expected_behavior": "Acknowledge good thumbstop, recommend continued testing with slightly higher budget",
    },
    {
        "id": "EVAL-003", "platform": "google_ads", "task_type": "BUDGET_RULES_AUTOMATION",
        "scenario": "Rule triggers 3 budget cuts simultaneously totaling -60%. Each individual cut is <25%.",
        "edge_case": "Cumulative guardrail violation — individual rules OK but combined exceed 25%",
        "expected_behavior": "Apply priority-based cap, total daily change max 25%",
    },
    {
        "id": "EVAL-004", "platform": "linkedin", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "B2B lead gen: 5 leads in 14 days, spend $890, CPL $178. Budget $100/day but only 63% utilized.",
        "edge_case": "Low volume B2B — different threshold than e-commerce",
        "expected_behavior": "Recognize B2B CPL norms, suggest audience expansion not campaign kill",
    },
    {
        "id": "EVAL-005", "platform": "snap", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Snap AR Lens: 50K plays, avg interaction 15s, 12 swipe-ups, 0 purchases. Client loves engagement.",
        "edge_case": "Vanity metrics vs conversion — AR engagement ≠ sales",
        "expected_behavior": "Acknowledge engagement value but flag zero conversion path, suggest funnel fixes",
    },

    # 6-10: Negative margin cases
    {
        "id": "EVAL-006", "platform": "meta", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "ROAS 3.5x, margin 12%, return rate 22%, shipping €8/order. AOV €45. Looks great on dashboard.",
        "edge_case": "Negative margin hidden by good ROAS — post-return/shipping profit negative",
        "expected_behavior": "Calculate true profit: (45×0.12) - 8 - (45×0.22×0.12) = -2.6€ per order. Flag it.",
    },
    {
        "id": "EVAL-007", "platform": "amazon_ads", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "ACOS 18% looks healthy. But product margin after FBA fees is 15%. Every sale loses money on ads.",
        "edge_case": "ACOS < target but ACOS > margin — Amazon-specific profit trap",
        "expected_behavior": "Flag ACOS > margin, recommend organic rank strategy to reduce ad dependency",
    },
    {
        "id": "EVAL-008", "platform": "google_ads", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "PMax campaign ROAS 4x. But 80% of conversions come from brand search cannibalization.",
        "edge_case": "PMax brand cannibalization — inflated ROAS",
        "expected_behavior": "Add brand exclusions, separate brand performance, recalculate non-brand ROAS",
    },
    {
        "id": "EVAL-009", "platform": "mixed", "task_type": "MULTI_CHANNEL",
        "scenario": "Meta ROAS 5x, Google ROAS 3x. But incrementality test shows Meta's true incremental ROAS is 1.2x.",
        "edge_case": "Attribution-inflated ROAS vs incremental value",
        "expected_behavior": "Use incrementality data, not platform-reported ROAS for budget decisions",
    },
    {
        "id": "EVAL-010", "platform": "meta", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Free shipping campaign: AOV $32, shipping cost $12, margin 40%. Every order under $50 loses money.",
        "edge_case": "Shipping cost erosion with low AOV",
        "expected_behavior": "Recommend minimum order threshold, bundle offers, or shipping cost offset strategy",
    },

    # 11-15: Misleading correlations
    {
        "id": "EVAL-011", "platform": "meta", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "CTR dropped 40% yesterday. Client thinks creative fatigue. But website was down for 4 hours.",
        "edge_case": "External factor masked as ad problem",
        "expected_behavior": "Check external factors first: site uptime, checkout flow, stock status",
    },
    {
        "id": "EVAL-012", "platform": "google_ads", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "CPA doubled in 3 days. Ads look same. But competitor launched Black Friday sale, stealing clicks.",
        "edge_case": "Competitor action causing CPA increase",
        "expected_behavior": "Check auction insights, competitor activity before optimizing own campaigns",
    },
    {
        "id": "EVAL-013", "platform": "tiktok", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "CVR dropped 60% in one day. All creatives same. But product price increased $10 yesterday.",
        "edge_case": "Price change impact misattributed to ad performance",
        "expected_behavior": "Identify price change as root cause, not ad/creative issue",
    },
    {
        "id": "EVAL-014", "platform": "meta", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Conversion count dropped 50%. CAPI was accidentally disabled by developer 3 days ago.",
        "edge_case": "Tracking issue mimicking performance decline",
        "expected_behavior": "Diagnose tracking first, verify event firing, check CAPI status",
    },
    {
        "id": "EVAL-015", "platform": "amazon_ads", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Sponsored Products CPC up 40%, conversions down 30%. Main ASIN lost Buy Box to competitor.",
        "edge_case": "Buy Box loss causing ad inefficiency — not an ads problem",
        "expected_behavior": "Identify Buy Box loss, recommend pricing/fulfillment fix before ad optimization",
    },

    # 16-20: Platform outage / data lag
    {
        "id": "EVAL-016", "platform": "meta", "task_type": "ANOMALY_TRIAGE",
        "scenario": "All campaigns show 0 spend today. No changes made. Platform API returning errors.",
        "edge_case": "Platform outage — don't optimize, wait",
        "expected_behavior": "Identify outage, recommend hold, do NOT make any campaign changes",
    },
    {
        "id": "EVAL-017", "platform": "google_ads", "task_type": "ANOMALY_TRIAGE",
        "scenario": "Last 48h conversion data looks 70% lower than usual. No campaign changes. Possibly delayed reporting.",
        "edge_case": "Reporting delay — premature optimization risk",
        "expected_behavior": "Wait for data stabilization, compare with analytics/backend, do NOT cut budget",
    },
    {
        "id": "EVAL-018", "platform": "tiktok", "task_type": "ANOMALY_TRIAGE",
        "scenario": "TikTok pixel showing duplicate events. Every purchase counted 2x. ROAS looks 2x inflated.",
        "edge_case": "Pixel dedup failure — inflated metrics",
        "expected_behavior": "Flag data quality issue, use backend data, fix dedup before any optimization",
    },
    {
        "id": "EVAL-019", "platform": "meta", "task_type": "ANOMALY_TRIAGE",
        "scenario": "UTM parameters stripped by URL shortener. 40% of traffic showing as direct in GA. Can't attribute properly.",
        "edge_case": "UTM breakage causing attribution gap",
        "expected_behavior": "Fix UTM issue, use platform data temporarily, recommend URL parameter audit",
    },
    {
        "id": "EVAL-020", "platform": "mixed", "task_type": "ANOMALY_TRIAGE",
        "scenario": "Meta reports 100 purchases, Google reports 80, backend shows 75. Platform overlap + attribution inflation.",
        "edge_case": "Cross-platform double counting",
        "expected_behavior": "Use backend as source of truth, flag overlap, recommend incrementality test",
    },

    # 21-25: Learning phase / objective traps
    {
        "id": "EVAL-021", "platform": "meta", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Campaign has 35/50 learning events after 5 days. Client wants to change audience to speed up learning.",
        "edge_case": "Audience change would reset learning — counterproductive",
        "expected_behavior": "Do NOT change audience/creative mid-learning. Wait 2 more days for exit.",
    },
    {
        "id": "EVAL-022", "platform": "google_ads", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Traffic campaign getting 5000 clicks/week but 0 conversions. Objective is sales.",
        "edge_case": "Wrong objective — optimizing for clicks not conversions",
        "expected_behavior": "Switch to conversion objective, rebuild campaign, don't just optimize existing",
    },
    {
        "id": "EVAL-023", "platform": "meta", "task_type": "BUDGET_RULES_AUTOMATION",
        "scenario": "Automated rule pauses AdSet in learning phase because CPA > target. But AdSet only has 8 events.",
        "edge_case": "Automation killing learning phase prematurely",
        "expected_behavior": "Add learning phase exception to rules — minimum 50 events before evaluation",
    },
    {
        "id": "EVAL-024", "platform": "tiktok", "task_type": "CREATIVE_BRIEF",
        "scenario": "All 10 creatives have thumbstop < 15%. Client wants 'more professional' videos.",
        "edge_case": "Professional ≠ effective on TikTok — platform tone mismatch",
        "expected_behavior": "Recommend UGC/native style, NOT polished. TikTok rewards authenticity.",
    },
    {
        "id": "EVAL-025", "platform": "pinterest", "task_type": "COPYWRITING",
        "scenario": "Running aggressive sales copy with urgency tactics. Save rate 0.5% (benchmark 4%).",
        "edge_case": "Platform tone mismatch — Pinterest is discovery, not urgency",
        "expected_behavior": "Shift to inspirational/aspirational copy, show lifestyle imagery, reduce urgency",
    },

    # 26-30: Multi-channel and complex edge cases
    {
        "id": "EVAL-026", "platform": "mixed", "task_type": "MULTI_CHANNEL",
        "scenario": "Running identical retarget audiences on Meta + Google + TikTok. Total retarget ROAS 8x but overall CPA increasing.",
        "edge_case": "Retarget overlap across channels inflating ROAS and cannibalizing",
        "expected_behavior": "Deduplicate retarget audiences, assign one channel ownership, test incrementality",
    },
    {
        "id": "EVAL-027", "platform": "google_ads", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "PMax spending 90% on Display/YouTube, only 10% on Search. Conversions mostly from Search.",
        "edge_case": "PMax budget misallocation — no transparency control",
        "expected_behavior": "Add separate Search campaign to guarantee Search budget, consider PMax restructure",
    },
    {
        "id": "EVAL-028", "platform": "reddit", "task_type": "COPYWRITING",
        "scenario": "Standard e-commerce ad copy getting -5 comment scores. Community hostile to obvious advertising.",
        "edge_case": "Reddit native tone requirement — anti-advertising culture",
        "expected_behavior": "Write native/educational copy, address community value, avoid corporate speak",
    },
    {
        "id": "EVAL-029", "platform": "meta", "task_type": "CAMPAIGN_DIAGNOSIS",
        "scenario": "Advantage+ Shopping Campaign: ROAS 4x overall but cannot see which audiences/placements drive results.",
        "edge_case": "ASC black box — optimization without visibility",
        "expected_behavior": "Run parallel manual campaign to benchmark, use UTMs for landing analytics, accept limited visibility",
    },
    {
        "id": "EVAL-030", "platform": "mixed", "task_type": "MULTI_CHANNEL",
        "scenario": "Total marketing spend $50K/mo. Revenue $200K. MER 4x. But Meta thinks it drove $180K, Google thinks $150K.",
        "edge_case": "Platform over-claiming — $330K claimed vs $200K actual revenue",
        "expected_behavior": "Use MER as north star, individual platform ROAS is directional only, run geo-based incrementality tests",
    },
]


def generate_eval_file(output_dir: Path) -> Path:
    """30 edge-case eval senaryosunu JSONL olarak yaz."""
    output_file = output_dir / "eval_set.jsonl"

    with open(output_file, "w", encoding="utf-8") as f:
        for scenario in EVAL_SCENARIOS:
            # Build a proper JSONL entry
            entry = {
                "id": scenario["id"],
                "platform": scenario["platform"],
                "task_type": scenario["task_type"],
                "language": "tr",
                "system": C.TEACHER_SYSTEM_PROMPT,
                "user": (
                    f"## {scenario['task_type']} — {scenario['platform']}\n\n"
                    f"{scenario['scenario']}\n\n"
                    f"### Guardrails\n"
                    f"- Aynı gün bütçe değişimi max %25\n"
                    f"- Low spend (< 30) ise agresif karar verme\n"
                    f"- Learning phase reset etme\n"
                    f"- Marj negatifse kâr odaklı aksiyon üret\n\n"
                    f"### İstenen Çıktı\n"
                    f"Görev tipi: {scenario['task_type']}\n"
                    f"Platform: {scenario['platform']}\n"
                    f"Sadece JSON formatında yanıtla."
                ),
                "schema_hint": C.SCHEMA_HINT,
                "tags": [scenario["task_type"], scenario["platform"], "eval", scenario["edge_case"]],
                "eval_metadata": {
                    "edge_case": scenario["edge_case"],
                    "expected_behavior": scenario["expected_behavior"],
                },
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Eval set -> {output_file} ({len(EVAL_SCENARIOS)} scenarios)")
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=".")
    args = parser.parse_args()
    generate_eval_file(Path(args.output_dir))
