"""
config.py — Dağılım oranları, guardrails, sabitler
===================================================
Tüm generator modülleri bu sabitleri import eder.
"""

# ──────────────────────────────────────────────
# TASK TYPE DISTRIBUTION  (toplam = 1.0)
# ──────────────────────────────────────────────
TASK_DISTRIBUTION: dict[str, float] = {
    "CAMPAIGN_DIAGNOSIS":       0.40,
    "COPYWRITING":              0.25,
    "CREATIVE_BRIEF":           0.10,
    "BUDGET_RULES_AUTOMATION":  0.10,
    "STRATEGY_PLAYBOOK":        0.03,
    "POST_MORTEM":              0.03,
    "LANDING_OFFER":            0.03,
    "ANOMALY_TRIAGE":           0.03,
    "MULTI_CHANNEL":            0.03,
}

# ──────────────────────────────────────────────
# PLATFORM DISTRIBUTION  (toplam = 1.0)
# ──────────────────────────────────────────────
PLATFORM_DISTRIBUTION: dict[str, float] = {
    "meta":        0.20,
    "google_ads":  0.20,
    "tiktok":      0.15,
    "mixed":       0.15,
    "x":           0.05,
    "linkedin":    0.05,
    "pinterest":   0.05,
    "snap":        0.05,
    "reddit":      0.03,
    "amazon_ads":  0.07,
}

# ──────────────────────────────────────────────
# SPECIAL SCENARIO FLAGS (overlay ratios)
# ──────────────────────────────────────────────
MISLEADING_CORRELATION_RATIO = 0.20   # %20 yanıltıcı korelasyon
PLATFORM_OUTAGE_RATIO        = 0.10   # %10 outage/delay/data lag
LOW_SPEND_GUARDRAIL_RATIO    = 0.15   # %15 low-spend guardrail
NEGATIVE_MARGIN_RATIO         = 0.10   # %10 marj negatif (ROAS iyi görünse bile)

# ──────────────────────────────────────────────
# GUARDRAILS
# ──────────────────────────────────────────────
MAX_SAME_DAY_BUDGET_CHANGE_PCT = 25          # Aynı gün max %25
LOW_SPEND_THRESHOLD            = 30.0        # Son 3 günde spend < 30 → agresif karar yok
LEARNING_PHASE_PROTECT         = True        # Learning phase reset etme
NEGATIVE_MARGIN_OVERRIDE       = True        # Marj negatifse ROAS iyi olsa bile kâr odaklı aksiyon

# ──────────────────────────────────────────────
# BRAND VOICE
# ──────────────────────────────────────────────
BRAND_VOICE_RULES = [
    "Premium, net, kısa yanıtlar",
    "Küfür yok",
    "Boş motivasyon yok",
    "Somut rakamlarla destekle",
    "Jenerik tavsiyelerden kaçın",
]

# ──────────────────────────────────────────────
# INDUSTRIES (sektörler)
# ──────────────────────────────────────────────
INDUSTRIES = [
    "fashion", "beauty", "electronics", "home_decor", "food_delivery",
    "saas_b2b", "fintech", "health_wellness", "automotive", "education",
    "travel", "gaming", "real_estate", "pet_supplies", "sports_fitness",
    "jewelry", "kids_baby", "grocery", "furniture", "subscription_box",
    "supplements", "outdoor_gear", "audio_tech", "smart_home", "luxury_goods",
    "coffee_tea", "organic_food", "diy_tools", "stationery", "vintage_clothing",
    "cycling", "yoga_meditation", "dental_care", "eyewear", "watches",
    "sustainable_fashion", "plant_based", "camping", "photography", "musical_instruments",
    "board_games", "craft_beer", "wine", "skincare_men", "maternity",
    "coworking", "legal_tech", "hr_tech", "logistics_saas", "insurtech",
]

# ──────────────────────────────────────────────
# COUNTRIES / GEO SETS
# ──────────────────────────────────────────────
COUNTRY_SETS = [
    # (country_code, country_name, currency, language_hint)
    ("TR", "Türkiye",        "TRY", "tr"),
    ("US", "United States",  "USD", "en"),
    ("DE", "Germany",        "EUR", "de"),
    ("UK", "United Kingdom", "GBP", "en"),
    ("FR", "France",         "EUR", "fr"),
    ("NL", "Netherlands",    "EUR", "nl"),
    ("IT", "Italy",          "EUR", "it"),
    ("ES", "Spain",          "EUR", "es"),
    ("SA", "Saudi Arabia",   "SAR", "ar"),
    ("AE", "UAE",            "AED", "ar"),
    ("JP", "Japan",          "JPY", "ja"),
    ("KR", "South Korea",    "KRW", "ko"),
    ("BR", "Brazil",         "BRL", "pt"),
    ("MX", "Mexico",         "MXN", "es"),
    ("AU", "Australia",      "AUD", "en"),
    ("CA", "Canada",         "CAD", "en"),
    ("IN", "India",          "INR", "en"),
    ("PL", "Poland",         "PLN", "pl"),
    ("SE", "Sweden",         "SEK", "sv"),
    ("NO", "Norway",         "NOK", "no"),
    ("DK", "Denmark",        "DKK", "da"),
    ("ID", "Indonesia",      "IDR", "id"),
    ("TH", "Thailand",       "THB", "th"),
    ("VN", "Vietnam",        "VND", "vi"),
    ("PH", "Philippines",    "PHP", "en"),
    ("NG", "Nigeria",        "NGN", "en"),
    ("ZA", "South Africa",   "ZAR", "en"),
    ("EG", "Egypt",          "EGP", "ar"),
    ("CL", "Chile",          "CLP", "es"),
    ("CO", "Colombia",       "COP", "es"),
]

# ──────────────────────────────────────────────
# PRODUCT TEMPLATES  (sektör → ürün listesi)
# ──────────────────────────────────────────────
PRODUCT_TEMPLATES: dict[str, list[dict]] = {
    "fashion": [
        {"name": "Premium Linen Blazer",       "price_range": (80, 350),  "margin_pct": (0.45, 0.70), "return_rate": (0.12, 0.25)},
        {"name": "Organic Cotton T-Shirt",     "price_range": (25, 65),   "margin_pct": (0.50, 0.75), "return_rate": (0.08, 0.18)},
        {"name": "Slim Fit Chinos",            "price_range": (40, 120),  "margin_pct": (0.40, 0.65), "return_rate": (0.15, 0.28)},
        {"name": "Merino Wool Sweater",        "price_range": (60, 200),  "margin_pct": (0.45, 0.68), "return_rate": (0.10, 0.20)},
        {"name": "Leather Crossbody Bag",      "price_range": (90, 400),  "margin_pct": (0.55, 0.78), "return_rate": (0.06, 0.14)},
        {"name": "Sustainable Denim Jacket",   "price_range": (70, 250),  "margin_pct": (0.42, 0.62), "return_rate": (0.10, 0.22)},
        {"name": "Silk Scarf",                 "price_range": (30, 150),  "margin_pct": (0.60, 0.82), "return_rate": (0.04, 0.10)},
        {"name": "Running Sneakers",           "price_range": (60, 180),  "margin_pct": (0.35, 0.55), "return_rate": (0.14, 0.30)},
    ],
    "beauty": [
        {"name": "Vitamin C Serum",            "price_range": (20, 80),   "margin_pct": (0.70, 0.88), "return_rate": (0.03, 0.08)},
        {"name": "Retinol Night Cream",        "price_range": (35, 120),  "margin_pct": (0.68, 0.85), "return_rate": (0.04, 0.10)},
        {"name": "Hyaluronic Acid Moisturizer","price_range": (25, 75),   "margin_pct": (0.72, 0.90), "return_rate": (0.02, 0.06)},
        {"name": "Mineral Sunscreen SPF50",    "price_range": (15, 45),   "margin_pct": (0.65, 0.82), "return_rate": (0.03, 0.07)},
        {"name": "Matte Lipstick Set",         "price_range": (18, 55),   "margin_pct": (0.75, 0.90), "return_rate": (0.05, 0.12)},
        {"name": "Hair Growth Oil",            "price_range": (22, 60),   "margin_pct": (0.70, 0.88), "return_rate": (0.06, 0.15)},
    ],
    "electronics": [
        {"name": "Wireless Noise-Cancel Headphones", "price_range": (80, 350),  "margin_pct": (0.25, 0.45), "return_rate": (0.08, 0.18)},
        {"name": "Smart Watch Fitness Tracker",      "price_range": (50, 200),  "margin_pct": (0.30, 0.50), "return_rate": (0.10, 0.20)},
        {"name": "Portable Bluetooth Speaker",       "price_range": (30, 120),  "margin_pct": (0.28, 0.48), "return_rate": (0.06, 0.14)},
        {"name": "USB-C Docking Station",            "price_range": (40, 150),  "margin_pct": (0.32, 0.52), "return_rate": (0.05, 0.12)},
        {"name": "Mechanical Keyboard RGB",          "price_range": (60, 200),  "margin_pct": (0.30, 0.50), "return_rate": (0.07, 0.15)},
        {"name": "4K Webcam",                        "price_range": (50, 180),  "margin_pct": (0.28, 0.45), "return_rate": (0.08, 0.16)},
    ],
    "saas_b2b": [
        {"name": "CRM Pro Monthly License",  "price_range": (49, 299),   "margin_pct": (0.80, 0.95), "return_rate": (0.0, 0.02)},
        {"name": "Project Mgmt Tool Annual",  "price_range": (120, 600),  "margin_pct": (0.82, 0.94), "return_rate": (0.0, 0.03)},
        {"name": "Data Analytics Platform",   "price_range": (199, 999),  "margin_pct": (0.78, 0.92), "return_rate": (0.0, 0.02)},
        {"name": "HR Onboarding Software",    "price_range": (79, 399),   "margin_pct": (0.80, 0.93), "return_rate": (0.0, 0.02)},
        {"name": "Cloud Security Suite",      "price_range": (149, 799),  "margin_pct": (0.75, 0.90), "return_rate": (0.0, 0.01)},
    ],
    "health_wellness": [
        {"name": "Collagen Peptides Powder",  "price_range": (25, 60),   "margin_pct": (0.60, 0.80), "return_rate": (0.04, 0.10)},
        {"name": "Yoga Mat Premium",          "price_range": (30, 90),   "margin_pct": (0.50, 0.70), "return_rate": (0.06, 0.14)},
        {"name": "Resistance Bands Set",      "price_range": (15, 45),   "margin_pct": (0.55, 0.75), "return_rate": (0.05, 0.12)},
        {"name": "Meditation App Annual",     "price_range": (40, 120),  "margin_pct": (0.85, 0.95), "return_rate": (0.0, 0.03)},
        {"name": "Protein Bar Variety Pack",  "price_range": (20, 50),   "margin_pct": (0.40, 0.60), "return_rate": (0.03, 0.08)},
    ],
    "food_delivery": [
        {"name": "Meal Kit Subscription",     "price_range": (35, 90),   "margin_pct": (0.20, 0.40), "return_rate": (0.02, 0.06)},
        {"name": "Gourmet Snack Box",         "price_range": (25, 60),   "margin_pct": (0.30, 0.50), "return_rate": (0.03, 0.08)},
        {"name": "Artisan Coffee Bundle",     "price_range": (20, 55),   "margin_pct": (0.35, 0.55), "return_rate": (0.02, 0.05)},
        {"name": "Organic Juice Cleanse",     "price_range": (40, 100),  "margin_pct": (0.25, 0.45), "return_rate": (0.04, 0.10)},
    ],
    "fintech": [
        {"name": "Premium Card Account",          "price_range": (0, 15),    "margin_pct": (0.60, 0.85), "return_rate": (0.0, 0.01)},
        {"name": "Investment App Pro Tier",        "price_range": (10, 50),   "margin_pct": (0.70, 0.90), "return_rate": (0.0, 0.02)},
        {"name": "Business Expense Tracker",       "price_range": (20, 80),   "margin_pct": (0.75, 0.92), "return_rate": (0.0, 0.02)},
        {"name": "Crypto Wallet Premium",          "price_range": (5, 30),    "margin_pct": (0.65, 0.88), "return_rate": (0.0, 0.01)},
    ],
    "home_decor": [
        {"name": "Handwoven Area Rug",         "price_range": (80, 400),  "margin_pct": (0.45, 0.68), "return_rate": (0.10, 0.22)},
        {"name": "Scented Candle Set",         "price_range": (20, 60),   "margin_pct": (0.60, 0.80), "return_rate": (0.04, 0.10)},
        {"name": "Minimalist Wall Shelf",      "price_range": (40, 150),  "margin_pct": (0.38, 0.58), "return_rate": (0.08, 0.18)},
        {"name": "Ceramic Planter Collection", "price_range": (25, 80),   "margin_pct": (0.50, 0.72), "return_rate": (0.06, 0.14)},
        {"name": "Linen Curtain Panel",        "price_range": (30, 120),  "margin_pct": (0.42, 0.65), "return_rate": (0.12, 0.25)},
    ],
    "education": [
        {"name": "Online Language Course",     "price_range": (30, 200),  "margin_pct": (0.80, 0.95), "return_rate": (0.02, 0.06)},
        {"name": "Coding Bootcamp Access",     "price_range": (200, 800), "margin_pct": (0.75, 0.92), "return_rate": (0.03, 0.08)},
        {"name": "STEM Kit for Kids",          "price_range": (25, 80),   "margin_pct": (0.45, 0.65), "return_rate": (0.05, 0.12)},
        {"name": "Professional Cert Prep",     "price_range": (100, 500), "margin_pct": (0.78, 0.93), "return_rate": (0.02, 0.05)},
    ],
    "travel": [
        {"name": "Carry-On Smart Luggage",     "price_range": (120, 350), "margin_pct": (0.35, 0.55), "return_rate": (0.08, 0.18)},
        {"name": "Travel Neck Pillow Deluxe",  "price_range": (25, 70),   "margin_pct": (0.50, 0.72), "return_rate": (0.06, 0.14)},
        {"name": "Packing Cube Set",           "price_range": (20, 50),   "margin_pct": (0.55, 0.75), "return_rate": (0.04, 0.10)},
        {"name": "Boutique Hotel Booking",     "price_range": (80, 400),  "margin_pct": (0.15, 0.30), "return_rate": (0.02, 0.06)},
    ],
}

# Diğer sektörler için generic fallback
_GENERIC_PRODUCTS = [
    {"name": "Premium Product A",  "price_range": (30, 200),  "margin_pct": (0.40, 0.65), "return_rate": (0.05, 0.15)},
    {"name": "Standard Product B", "price_range": (15, 100),  "margin_pct": (0.35, 0.60), "return_rate": (0.06, 0.18)},
    {"name": "Budget Product C",   "price_range": (8, 50),    "margin_pct": (0.30, 0.55), "return_rate": (0.08, 0.20)},
    {"name": "Luxury Product D",   "price_range": (100, 500), "margin_pct": (0.50, 0.75), "return_rate": (0.04, 0.12)},
    {"name": "Subscription Tier",  "price_range": (10, 80),   "margin_pct": (0.70, 0.90), "return_rate": (0.02, 0.06)},
]

def get_products(industry: str) -> list[dict]:
    """Sektöre göre ürün listesi döndür. Bulunamazsa generic fallback."""
    return PRODUCT_TEMPLATES.get(industry, _GENERIC_PRODUCTS)


# ──────────────────────────────────────────────
# PROBLEM TYPES  (senaryo çeşitliliği)
# ──────────────────────────────────────────────
PROBLEM_TYPES = [
    "high_cpa_low_conversions",
    "ctr_drop_sudden",
    "creative_fatigue",
    "audience_saturation",
    "budget_overspend",
    "budget_underspend",
    "learning_phase_stuck",
    "roas_decline_gradual",
    "roas_spike_then_crash",
    "frequency_too_high",
    "cpm_inflation",
    "low_impression_share",
    "quality_score_drop",
    "landing_page_bounce",
    "checkout_drop_off",
    "stock_out_during_campaign",
    "price_change_impact",
    "seasonal_demand_shift",
    "competitor_bid_war",
    "attribution_mismatch",
    "pixel_tracking_broken",
    "capi_event_dedup_issue",
    "utm_parameter_missing",
    "reporting_delay_48h",
    "platform_outage_suspected",
    "data_lag_3_day",
    "margin_negative_roas_ok",
    "high_return_rate_hidden",
    "shipping_cost_eating_margin",
    "cross_channel_cannibalization",
    "audience_overlap_waste",
    "incrementality_question",
    "video_low_thumbstop",
    "video_high_view_low_convert",
    "hook_fatigue",
    "wrong_objective_setup",
    "broad_match_waste",
    "brand_vs_nonbrand_imbalance",
    "feed_disapprovals",
    "buy_box_lost",
    "new_market_cold_start",
]

# ──────────────────────────────────────────────
# TIME WINDOWS
# ──────────────────────────────────────────────
TIME_WINDOWS = [3, 7, 14, 30]

# ──────────────────────────────────────────────
# CAMPAIGN OBJECTIVES
# ──────────────────────────────────────────────
CAMPAIGN_OBJECTIVES = [
    "conversions", "purchase", "lead_generation", "app_install",
    "traffic", "awareness", "video_views", "engagement",
    "catalog_sales", "store_visits", "reach", "brand_awareness",
]

# ──────────────────────────────────────────────
# BIDDING STRATEGIES
# ──────────────────────────────────────────────
BIDDING_STRATEGIES = [
    "lowest_cost", "cost_cap", "bid_cap", "target_roas",
    "target_cpa", "maximize_conversions", "maximize_clicks",
    "manual_cpc", "enhanced_cpc", "value_based",
]

# ──────────────────────────────────────────────
# AUDIENCE TYPES
# ──────────────────────────────────────────────
AUDIENCE_TYPES = [
    "broad", "interest_based", "lookalike_1pct", "lookalike_3pct",
    "lookalike_5pct", "retargeting_30d", "retargeting_7d",
    "retargeting_180d", "custom_audience_email", "custom_audience_web",
    "in_market", "affinity", "demographic", "keyword_targeted",
    "topic_targeted", "placement_targeted", "job_title_targeted",
    "company_size_targeted", "community_targeted", "hashtag_targeted",
]

# ──────────────────────────────────────────────
# CREATIVE FORMATS
# ──────────────────────────────────────────────
CREATIVE_FORMATS = [
    "single_image", "carousel", "video_15s", "video_30s", "video_60s",
    "ugc_video", "collection", "instant_experience", "lead_form",
    "responsive_search_ad", "responsive_display", "shopping_product",
    "pmax_asset_group", "spark_ad", "dynamic_product_ad",
    "story_ad", "reel_ad", "pin_ad", "snap_ad", "promoted_post",
    "sponsored_product", "sponsored_brand", "sponsored_display",
]

# ──────────────────────────────────────────────
# SYSTEM PROMPT (teacher'a verilecek)
# ──────────────────────────────────────────────
TEACHER_SYSTEM_PROMPT = (
    "Sen bir reklam optimizasyon uzmanısın. "
    "Sadece geçerli JSON döndür — metin yok, açıklama yok, markdown yok. "
    "Yanıtın doğrudan '{' ile başla ve '}' ile bitir. "
    "Guardrails: "
    "(1) Aynı gün bütçe değişimi max %25. "
    "(2) Son 3 günde spend < 30 ise agresif karar verme, ölçüm/deney öner. "
    "(3) Learning phase / exploration reset etme (gerekmedikçe). "
    "(4) Marj negatifse ROAS iyi olsa bile kâr odaklı aksiyon üret. "
    "(5) Brand voice: premium, net, kısa; küfür yok; boş motivasyon yok."
)

SCHEMA_HINT = (
    'JSON şeması: {"id","platform","task_type","summary","diagnosis":[],'
    '"actions":[{"priority":"P0|P1|P2","scope","action","entity_ref","change","reason","guardrail","expected_impact"}],'
    '"experiments":[{"hypothesis","test","metric","success_threshold","duration_days"}],'
    '"risks":[],"questions_to_ask":[max 3]}. '
    'COPYWRITING ek: "ad_copies":[{"angle","primary","headline","cta","format","platform_tone_notes"}]. '
    'CREATIVE_BRIEF ek: "video_script":[{"sec","visual","voice","on_screen_text","edit_notes"}]. '
    'BUDGET_RULES_AUTOMATION ek: "rules_json":[{"if":{},"then":{},"safety":{}}].'
)

# ──────────────────────────────────────────────
# BATCH CONFIG
# ──────────────────────────────────────────────
DEFAULT_TOTAL_EXAMPLES = 1_000_000
DEFAULT_BATCH_SIZE     = 50_000
