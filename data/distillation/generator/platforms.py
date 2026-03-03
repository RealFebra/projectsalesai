"""
platforms.py — Platform-Specific Adapters
==========================================
Her platformun özel bileşenlerini, terminoloji farklarını ve
senaryo parametrelerini tanımlar.
"""

import random
from typing import Any


# ──────────────────────────────────────────────
# PLATFORM REGISTRY
# ──────────────────────────────────────────────

PLATFORM_CONFIGS: dict[str, dict[str, Any]] = {

    "meta": {
        "display_name": "Meta Ads",
        "entity_names": {"adgroup": "AdSet", "ad": "Ad"},
        "special_features": [
            "Advantage+ Shopping Campaign (ASC)",
            "Advantage+ Audience (broad)",
            "Dynamic Creative Optimization (DCO)",
            "Catalog Advantage+",
            "Placement Advantage+ (auto)",
        ],
        "placements": [
            "Facebook Feed", "Instagram Feed", "Instagram Stories",
            "Instagram Reels", "Facebook Marketplace", "Audience Network",
            "Messenger Inbox", "Facebook Right Column",
        ],
        "bidding_options": ["Lowest Cost", "Cost Cap", "Bid Cap", "Minimum ROAS"],
        "learning_phase": True,
        "learning_phase_events": 50,
        "attribution_windows": ["1d_click", "7d_click", "1d_view", "7d_click_1d_view"],
        "typical_issues": [
            "creative_fatigue", "learning_phase_stuck", "audience_saturation",
            "frequency_too_high", "broad_vs_interest_debate", "ios_att_signal_loss",
            "advantage_plus_transparency", "placement_dilution",
        ],
        "cpm_range": (4.0, 30.0),
        "ctr_range": (0.6, 3.5),
        "cvr_range": (0.8, 6.0),
        "has_video_metrics": True,
        "has_search_metrics": False,
        "has_shopping_metrics": True,
    },

    "google_ads": {
        "display_name": "Google Ads",
        "entity_names": {"adgroup": "AdGroup", "ad": "Ad", "keyword": "Keyword", "asset_group": "AssetGroup"},
        "special_features": [
            "Performance Max (PMax)",
            "Responsive Search Ads (RSA)",
            "Dynamic Search Ads (DSA)",
            "Shopping Feed / Merchant Center",
            "Brand restrictions in PMax",
            "Search Themes",
        ],
        "placements": [
            "Search", "Shopping", "Display Network", "YouTube",
            "Discover", "Gmail", "Maps",
        ],
        "bidding_options": [
            "Maximize Conversions", "Target CPA", "Target ROAS",
            "Maximize Clicks", "Manual CPC", "Enhanced CPC",
            "Maximize Conversion Value",
        ],
        "learning_phase": True,
        "learning_phase_events": 30,
        "attribution_windows": ["last_click", "data_driven", "first_click", "linear", "time_decay"],
        "typical_issues": [
            "broad_match_waste", "brand_vs_nonbrand_imbalance", "low_impression_share",
            "quality_score_drop", "pmax_cannibalization", "feed_disapprovals",
            "search_term_irrelevancy", "rsa_poor_combinations",
        ],
        "cpm_range": (2.0, 45.0),
        "ctr_range": (1.0, 8.0),
        "cvr_range": (1.0, 10.0),
        "has_video_metrics": True,
        "has_search_metrics": True,
        "has_shopping_metrics": True,
    },

    "tiktok": {
        "display_name": "TikTok Ads",
        "entity_names": {"adgroup": "AdGroup", "ad": "Ad"},
        "special_features": [
            "Spark Ads (organic boost)",
            "Smart Creative",
            "Dynamic Scene",
            "Video Shopping Ads (VSA)",
            "Search Ads (beta)",
        ],
        "placements": [
            "TikTok For You Feed", "TikTok Search", "TikTok Profile",
            "Pangle", "Global App Bundle",
        ],
        "bidding_options": ["Lowest Cost", "Cost Cap", "Bid Cap", "Minimum ROAS"],
        "learning_phase": True,
        "learning_phase_events": 50,
        "attribution_windows": ["1d_click", "7d_click", "1d_view"],
        "typical_issues": [
            "hook_fatigue", "video_low_thumbstop", "creative_iteration_velocity",
            "spark_ad_permission_expired", "audience_too_narrow",
            "high_frequency_short_lifecycle",
        ],
        "cpm_range": (3.0, 20.0),
        "ctr_range": (0.5, 3.0),
        "cvr_range": (0.3, 5.0),
        "has_video_metrics": True,
        "has_search_metrics": False,
        "has_shopping_metrics": False,
    },

    "x": {
        "display_name": "X (Twitter) Ads",
        "entity_names": {"adgroup": "AdGroup", "ad": "Ad"},
        "special_features": [
            "Promoted Ads",
            "Follower Ads",
            "Twitter Amplify",
            "Trend Takeover",
        ],
        "placements": [
            "Timeline", "Search Results", "Profile", "Replies",
        ],
        "bidding_options": ["Auto Bid", "Maximum Bid", "Target Cost"],
        "learning_phase": False,
        "attribution_windows": ["1d_click", "7d_click", "1d_view", "post_engagement"],
        "typical_issues": [
            "engagement_vs_conversion_gap", "brand_safety_concerns",
            "low_scale_available", "creative_angle_testing",
        ],
        "cpm_range": (4.0, 25.0),
        "ctr_range": (0.3, 2.5),
        "cvr_range": (0.2, 3.0),
        "has_video_metrics": True,
        "has_search_metrics": False,
        "has_shopping_metrics": False,
    },

    "linkedin": {
        "display_name": "LinkedIn Ads",
        "entity_names": {"adgroup": "Campaign", "ad": "Ad"},
        "special_features": [
            "Lead Gen Forms",
            "Conversation Ads",
            "Document Ads",
            "Event Ads",
            "LinkedIn Audience Network",
        ],
        "placements": [
            "LinkedIn Feed", "LinkedIn Audience Network", "LinkedIn Messaging",
        ],
        "bidding_options": ["Maximum Delivery", "Manual Bidding", "Target Cost"],
        "learning_phase": True,
        "learning_phase_events": 15,
        "attribution_windows": ["30d_click", "7d_view", "90d_click"],
        "typical_issues": [
            "high_cpl", "narrow_audience_exhaustion", "job_title_targeting_cost",
            "seniority_mismatch", "low_engagement_sponsored_content",
        ],
        "cpm_range": (20.0, 90.0),
        "ctr_range": (0.3, 1.2),
        "cvr_range": (1.0, 8.0),
        "has_video_metrics": True,
        "has_search_metrics": False,
        "has_shopping_metrics": False,
        "b2b_specific": True,
        "b2b_segments": [
            "C-Suite", "VP", "Director", "Manager", "Individual Contributor",
        ],
        "company_sizes": [
            "1-10", "11-50", "51-200", "201-500", "501-1000",
            "1001-5000", "5001-10000", "10000+",
        ],
    },

    "pinterest": {
        "display_name": "Pinterest Ads",
        "entity_names": {"adgroup": "AdGroup", "ad": "Pin"},
        "special_features": [
            "Shopping Pins",
            "Idea Pins (organic→paid)",
            "Pinterest Trends integration",
            "Catalog ingestion",
        ],
        "placements": [
            "Home Feed", "Search Results", "Related Pins",
        ],
        "bidding_options": ["Automatic", "Custom (CPC)", "Custom (CPM)"],
        "learning_phase": True,
        "learning_phase_events": 20,
        "attribution_windows": ["30d_click", "1d_view", "7d_click"],
        "typical_issues": [
            "low_save_rate", "discovery_intent_mismatch", "creative_aesthetic_off",
            "seasonal_pin_timing", "catalog_sync_issues",
        ],
        "cpm_range": (3.0, 18.0),
        "ctr_range": (0.3, 2.0),
        "cvr_range": (0.5, 4.0),
        "has_video_metrics": True,
        "has_search_metrics": False,
        "has_shopping_metrics": True,
        "extra_metrics": ["save_rate", "closeup_rate"],
    },

    "snap": {
        "display_name": "Snapchat Ads",
        "entity_names": {"adgroup": "Ad Squad", "ad": "Ad"},
        "special_features": [
            "AR Lens Ads",
            "Story Ads",
            "Collection Ads",
            "Dynamic Ads",
            "Spotlight Ads",
        ],
        "placements": [
            "Between Stories", "Discover Feed", "Spotlight",
            "Snap Map", "Camera (AR Lens)",
        ],
        "bidding_options": ["Auto-Bid", "Target Cost", "Max Bid"],
        "learning_phase": True,
        "learning_phase_events": 50,
        "attribution_windows": ["1d_swipe_up", "7d_swipe_up", "1d_view", "28d_swipe_up"],
        "typical_issues": [
            "swipe_up_rate_low", "young_demo_limited_purchasing",
            "ar_lens_engagement_no_conversion", "story_completion_rate",
        ],
        "cpm_range": (2.0, 15.0),
        "ctr_range": (0.3, 2.0),
        "cvr_range": (0.2, 3.0),
        "has_video_metrics": True,
        "has_search_metrics": False,
        "has_shopping_metrics": False,
        "extra_metrics": ["swipe_up_rate", "story_completion_rate"],
    },

    "reddit": {
        "display_name": "Reddit Ads",
        "entity_names": {"adgroup": "AdGroup", "ad": "Ad"},
        "special_features": [
            "Community Targeting (subreddits)",
            "Conversation Ads",
            "Free-Form Ads",
            "Reddit Pixel + CAPI",
        ],
        "placements": [
            "Feed", "Conversation Thread", "Search Results",
        ],
        "bidding_options": ["Automatic", "CPC Manual", "CPM Manual", "CPV Manual"],
        "learning_phase": False,
        "attribution_windows": ["1d_click", "7d_click", "1d_view"],
        "typical_issues": [
            "native_tone_mismatch", "community_backlash", "comment_sentiment_negative",
            "low_scale_niche_subreddits", "ad_fatigue_small_community",
        ],
        "cpm_range": (2.0, 12.0),
        "ctr_range": (0.3, 2.5),
        "cvr_range": (0.3, 4.0),
        "has_video_metrics": True,
        "has_search_metrics": False,
        "has_shopping_metrics": False,
        "extra_metrics": ["comment_upvote_ratio", "subreddit_engagement_rate"],
    },

    "amazon_ads": {
        "display_name": "Amazon Ads",
        "entity_names": {"adgroup": "AdGroup", "ad": "Ad", "product_group": "ProductGroup", "keyword": "Keyword"},
        "special_features": [
            "Sponsored Products",
            "Sponsored Brands",
            "Sponsored Display",
            "Amazon DSP",
            "Brand Analytics / Search Query Report",
        ],
        "placements": [
            "Search Top of Page", "Search Rest of Page",
            "Product Detail Page", "Off-Amazon (DSP)",
        ],
        "bidding_options": [
            "Dynamic Bids Down Only", "Dynamic Bids Up and Down",
            "Fixed Bids", "Rule-Based Bidding",
        ],
        "learning_phase": False,
        "attribution_windows": ["7d_click", "14d_click"],
        "typical_issues": [
            "acos_too_high", "tacos_creeping", "buy_box_lost",
            "catalog_suppressed", "competitor_conquesting",
            "brand_defense_cost", "new_to_brand_low",
        ],
        "cpm_range": (3.0, 25.0),
        "ctr_range": (0.3, 3.0),
        "cvr_range": (2.0, 15.0),
        "has_video_metrics": False,
        "has_search_metrics": True,
        "has_shopping_metrics": True,
        "extra_metrics": ["acos", "tacos", "buy_box_pct", "new_to_brand_pct"],
    },

    "mixed": {
        "display_name": "Multi-Channel (Mixed)",
        "entity_names": {"adgroup": "AdSet/AdGroup", "ad": "Ad"},
        "special_features": [
            "Cross-channel attribution",
            "Budget split optimization",
            "Incrementality testing",
            "Audience dedup across platforms",
        ],
        "placements": ["Cross-Platform"],
        "bidding_options": ["Platform-native"],
        "learning_phase": False,
        "attribution_windows": ["platform_native", "last_click_cross", "data_driven_cross"],
        "typical_issues": [
            "cross_channel_cannibalization", "audience_overlap_waste",
            "incrementality_question", "budget_allocation_suboptimal",
            "attribution_double_counting", "reporting_discrepancy",
        ],
        "cpm_range": (3.0, 30.0),
        "ctr_range": (0.5, 4.0),
        "cvr_range": (0.5, 8.0),
        "has_video_metrics": True,
        "has_search_metrics": True,
        "has_shopping_metrics": True,
    },
}


def get_platform_config(platform: str) -> dict[str, Any]:
    """Platform konfigürasyonu döndürür."""
    return PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["meta"])


def pick_platform_issue(platform: str) -> str:
    """Platformun tipik sorunlarından birini rastgele seç."""
    cfg = get_platform_config(platform)
    return random.choice(cfg["typical_issues"])


def pick_placement(platform: str) -> str:
    """Rastgele placement seç."""
    cfg = get_platform_config(platform)
    return random.choice(cfg["placements"])


def pick_attribution_window(platform: str) -> str:
    """Rastgele attribution window seç."""
    cfg = get_platform_config(platform)
    return random.choice(cfg["attribution_windows"])


def pick_bidding(platform: str) -> str:
    """Rastgele bidding strategy seç."""
    cfg = get_platform_config(platform)
    return random.choice(cfg["bidding_options"])


def pick_special_feature(platform: str) -> str:
    """Rastgele special feature seç."""
    cfg = get_platform_config(platform)
    return random.choice(cfg["special_features"])


def has_learning_phase(platform: str) -> bool:
    """Platform learning phase mekanizmasına sahip mi?"""
    return get_platform_config(platform).get("learning_phase", False)


def get_metric_ranges(platform: str) -> dict:
    """Platform için CPM/CTR/CVR ranges döndürür."""
    cfg = get_platform_config(platform)
    return {
        "cpm_range": cfg["cpm_range"],
        "ctr_range": cfg["ctr_range"],
        "cvr_range": cfg["cvr_range"],
    }


def generate_mixed_platform_context() -> dict:
    """Mixed senaryo için 2-3 platform seçip her biri için ayrı metrikler üret."""
    n_platforms = random.choice([2, 2, 2, 3])
    real_platforms = [p for p in PLATFORM_CONFIGS if p != "mixed"]
    chosen = random.sample(real_platforms, n_platforms)

    channels = {}
    for plat in chosen:
        ranges = get_metric_ranges(plat)
        from .schemas import generate_coherent_metrics
        m = generate_coherent_metrics(
            cpm_range=ranges["cpm_range"],
            ctr_range=ranges["ctr_range"],
            cvr_range=ranges["cvr_range"],
        )
        budget_share = round(random.uniform(0.15, 0.60), 2)
        channels[plat] = {
            "metrics": m,
            "budget_share_pct": round(budget_share * 100, 1),
        }

    # Normalize budget shares to 100%
    total_share = sum(c["budget_share_pct"] for c in channels.values())
    for plat in channels:
        channels[plat]["budget_share_pct"] = round(
            channels[plat]["budget_share_pct"] / total_share * 100, 1
        )

    return {"channels": channels, "platforms": chosen}


# ──────────────────────────────────────────────
# PLATFORM-SPECIFIC SCENARIO ELEMENTS
# ──────────────────────────────────────────────

def get_platform_scenario_elements(platform: str) -> dict:
    """
    Platforma özgü senaryo öğeleri döndürür.
    Bu öğeler user promptlarına eklenir.
    """
    elements: dict[str, Any] = {"platform": platform}

    if platform == "meta":
        elements["adset_structure"] = random.choice([
            "3 AdSet: Broad, Interest (Fashion + Lifestyle), LAL 1%",
            "4 AdSet: LAL 1%, LAL 3%, Interest Stack, Retarget 30d",
            "2 AdSet: ASC (Advantage+ Shopping), Manual Retarget 7d",
            "5 AdSet: Broad 18-34, Broad 35-54, Interest, LAL 2%, Retarget",
        ])
        elements["creative_status"] = random.choice([
            "6 active creatives — 2 video, 3 image, 1 carousel; en iyi video 5 gündür aktif",
            "4 active creatives — 3 UGC video, 1 static; UGC#1 fatigued (frequency 8.2)",
            "8 active creatives — DCO enabled, 3 headline × 3 image combo",
            "3 active creatives — 1 Reel format, 1 Stories, 1 Feed; Reel en iyi CTR",
        ])
        elements["learning_info"] = random.choice([
            "Prospecting AdSet learning phase'de — 22/50 event",
            "Tüm AdSet'ler learning phase'i geçmiş",
            "Yeni AdSet 3 gün önce eklendi — henüz 8 event",
            "ASC campaign learning complete, manual campaign learning'de",
        ])

    elif platform == "google_ads":
        elements["campaign_structure"] = random.choice([
            "3 Campaign: Brand Search, Non-Brand Search, PMax",
            "4 Campaign: Brand, Generic Search, Shopping, PMax (tCPA)",
            "2 Campaign: PMax (full), Brand Exact Match",
            "5 Campaign: Brand, Non-Brand, DSA, Shopping Standard, PMax",
        ])
        elements["keyword_snapshot"] = random.choice([
            "Top 5 KW: [brand] CPC $0.8, [brand shoe] $1.2, +running +shoes $3.4, \"best sneakers\" $4.1, +buy +sneakers +online $2.8",
            "Top 5 KW: [brand] $0.5, +crm +software $18.2, \"project management tool\" $12.5, +best +crm $15.8, [brand crm] $0.9",
            "PMax search terms: 40% brand, 30% generic, 20% competitor, 10% irrelevant",
            "Non-brand impression share: 22% — lost to rank 45%, lost to budget 33%",
        ])
        elements["quality_info"] = random.choice([
            "Avg QS: 6.2 — ad relevance Above Avg, landing exp Below Avg",
            "Avg QS: 4.8 — expected CTR Below Avg, ad relevance Avg",
            "Avg QS: 7.5 — all components Above Avg except landing",
            "Avg QS: 3.1 — tüm bileşenler Below Avg, acil landing page iyileştirme gerekli",
        ])

    elif platform == "tiktok":
        elements["creative_velocity"] = random.choice([
            "Son 14 günde 12 yeni creative test edildi — 3 winner, 9 killed",
            "Son 7 günde creative yenilemesi yok — en iyi hook 10 gündür aynı",
            "20 creative havuzu — thumbstop rate: top 3 > %35, bottom 10 < %12",
            "Spark Ads: 3 organik post boost edildi — 1'i viral (2M view), diğerleri düşük",
        ])
        elements["hook_analysis"] = random.choice([
            "Hook A: 'Did you know...' — thumbstop %42, VTR %18; Hook B: product demo — thumbstop %28, VTR %25",
            "UGC hook > polished hook (thumbstop +15pp) ama CVR benzer",
            "İlk 2 saniye face-to-camera en iyi thumbstop (%48) ama düşük CVR (%0.8)",
            "Text overlay hook > voiceover hook — thumbstop +8pp, CPA -22%",
        ])

    elif platform == "linkedin":
        elements["audience_targeting"] = random.choice([
            "Job Title: Marketing Manager, CMO, Head of Growth | Company Size: 201-1000 | Seniority: Director+",
            "Skills: SaaS, B2B Marketing, Growth Hacking | Industry: Tech, FinTech | Seniority: VP+",
            "Job Function: IT, Engineering | Company Size: 1001-5000 | Geo: DACH region",
            "Matched Audience: Website retarget (90d) + Contact list upload (12K emails)",
        ])
        elements["lead_gen_info"] = random.choice([
            "Lead Gen Form: 4 fields (name, email, company, job title) — form fill rate %12",
            "Lead Gen Form: 7 fields — form fill rate %4.8, high quality but low volume",
            "Website conversion: demo request page — CVR %2.1 from LinkedIn clicks",
            "Conversation Ad funnel: 3-step flow — completion rate %8.5",
        ])

    elif platform == "amazon_ads":
        elements["catalog_status"] = random.choice([
            "150 active SKUs — 12 suppressed (image quality), 8 Buy Box lost to competitor",
            "85 SKUs — all active, Buy Box: %92, top ASIN contributes %35 of revenue",
            "320 SKUs — 45 suppressed, feed health %86, 15 pricing errors",
            "60 SKUs — parent-child setup issues, 5 ASINs not showing in search",
        ])
        elements["acos_info"] = random.choice([
            "Sponsored Products ACOS: %28 (target: %22), TACOS: %12",
            "SP ACOS: %15 (healthy), SB ACOS: %42 (bleeding), SD ACOS: %35",
            "Overall ACOS: %32, brand defense ACOS: %8, conquesting ACOS: %55",
            "TACOS: %18 — organic rank improving, reducing SP dependency possible",
        ])

    elif platform == "pinterest":
        elements["pin_metrics"] = random.choice([
            "Save Rate: %2.1 (benchmark %4), Closeup Rate: %8.5",
            "Top pin: Save Rate %6.8, Closeup %12 — lifestyle imagery outperforms product-only",
            "Idea Pins: high engagement (avg save %5.2) ama traffic düşük",
            "Shopping Pins: CTR %1.8. Catalog sync 2h delayed — 30 products stale price",
        ])

    elif platform == "snap":
        elements["snap_metrics"] = random.choice([
            "Swipe-Up Rate: %1.2, Story Completion: %45, AR Lens plays: 28K",
            "Swipe-Up Rate: %0.6 (low), demo 18-24 predominant (%78)",
            "AR Lens: 50K plays, avg lens time 12s, shareability rate %8",
            "Collection Ad: swipe rate %2.1, product tap rate %0.8",
        ])

    elif platform == "reddit":
        elements["reddit_context"] = random.choice([
            "Subreddits: r/SkincareAddiction (2.3M), r/BeautyGuRu (400K) — native tone required",
            "Subreddits: r/buildapcsales (1.5M), r/pcmasterrace (7M) — comment sentiment mixed",
            "Promoted post: 82 upvotes, 15 comments (60% positive, 40% sceptical)",
            "Community targeting: 5 subreddits — 2 performing well, 3 negative sentiment",
        ])

    return elements


# ──────────────────────────────────────────────
# CAMPAIGN NAME GENERATOR
# ──────────────────────────────────────────────

_CAMPAIGN_PREFIXES = [
    "Prospecting", "Retargeting", "Brand_Awareness", "Conversion",
    "Cold_Audience", "Warm_Audience", "Hot_Audience", "Loyalty",
    "Acquisition", "Winback", "Launch", "Seasonal", "Flash_Sale",
    "Evergreen", "Top_Funnel", "Mid_Funnel", "Bottom_Funnel",
    "Discovery", "Consideration", "Performance_Max",
]

_GEO_SUFFIXES = [
    "TR", "US", "DE", "UK", "FR", "EU", "DACH", "MENA", "APAC",
    "LATAM", "Global", "Nordics", "Benelux", "SEA",
]


def generate_campaign_name() -> str:
    """Rastgele gerçekçi kampanya adı üret."""
    prefix = random.choice(_CAMPAIGN_PREFIXES)
    geo = random.choice(_GEO_SUFFIXES)
    suffix = random.choice(["", "_v2", "_test", "_scale", "_Q1", "_Q2", "_Q3", "_Q4"])
    return f"{prefix}_{geo}{suffix}"


def generate_adgroup_name(platform: str) -> str:
    """Rastgele AdSet/AdGroup adı üret."""
    label = get_platform_config(platform)["entity_names"]["adgroup"]
    audience = random.choice([
        "Broad_18-34", "Broad_25-54", "Interest_Fashion", "Interest_Tech",
        "LAL_1pct", "LAL_3pct", "Retarget_7d", "Retarget_30d",
        "Custom_Email", "InMarket_Buyers", "Keyword_Exact",
        "Keyword_Broad", "Community_Reddit", "JobTitle_Director",
    ])
    return f"{label}:{audience}"


def generate_ad_name() -> str:
    """Rastgele Ad/Creative adı üret."""
    creative_type = random.choice([
        "UGC_Hook_A", "Static_Lifestyle_01", "Video_Demo_15s",
        "Carousel_Products", "RSA_v3", "DPA_Catalog", "Reel_Testimonial",
        "Story_BTS", "Pin_Flat_Lay", "Snap_AR_Try", "Spark_Organic_Boost",
    ])
    return f"Ad:{creative_type}"
