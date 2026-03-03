"""
scenarios.py — Senaryo Şablon Motoru
=====================================
Business context, metrik, problem ve breakdown gibi senaryo bileşenlerini
birleştirerek user promptu oluşturur.
"""

import random
import json
from typing import Any

from . import config as C
from . import schemas as S
from . import platforms as P


# ──────────────────────────────────────────────
# BUSINESS CONTEXT GENERATOR
# ──────────────────────────────────────────────

def _pick_business_context() -> dict:
    """Rastgele iş bağlamı üret."""
    industry = random.choice(C.INDUSTRIES)
    products = C.get_products(industry)
    product = random.choice(products)
    country_set = random.choice(C.COUNTRY_SETS)
    code, name, currency, lang = country_set

    price = round(random.uniform(*product["price_range"]), 2)
    margin_pct = round(random.uniform(*product["margin_pct"]), 2)
    return_rate = round(random.uniform(*product["return_rate"]), 2)

    shipping_cost = round(random.uniform(0, price * 0.15), 2)
    stock_status = random.choices(
        ["in_stock", "low_stock", "partial_oos", "seasonal_oos"],
        weights=[0.60, 0.20, 0.12, 0.08],
    )[0]

    return {
        "industry": industry,
        "product_name": product["name"],
        "price": price,
        "currency": currency,
        "margin_pct": margin_pct,
        "return_rate_pct": round(return_rate * 100, 1),
        "shipping_cost": shipping_cost,
        "country": name,
        "country_code": code,
        "stock_status": stock_status,
        "target_kpi": random.choice(["ROAS", "CPA", "Profit", "Revenue", "Leads"]),
    }


# ──────────────────────────────────────────────
# PROBLEM STATEMENT GENERATOR
# ──────────────────────────────────────────────

_PROBLEM_TEMPLATES: dict[str, list[str]] = {
    "high_cpa_low_conversions": [
        "Son {window} günde CPA {cpa_val} {currency} seviyesine çıktı, hedef {target_cpa} {currency}. Dönüşüm sayısı {purchases} ile hedefin çok altında.",
        "CPA target üzerinde seyrediyor ({cpa_val} vs hedef {target_cpa}). Conversion volume düşük ({purchases} purchase in {window}d).",
    ],
    "ctr_drop_sudden": [
        "CTR son {window} günde {ctr_before}%'dan {ctr_after}%'a düştü. Impression hacmi stabil ama click'ler %{drop_pct} geriledi.",
        "Ani CTR düşüşü: {ctr_before}% → {ctr_after}%. Creative değişikliği yapılmadı. Audience veya seasonal bir etki olabilir.",
    ],
    "creative_fatigue": [
        "En iyi creative'in frequency'si {freq} seviyesinde. CTR {ctr}%'a düştü (başlangıç: {ctr_start}%). Yeni creative gerekebilir.",
        "Top performing ad {days_active} gündür aktif, frequency {freq}. Performance plateau — CTR ve CVR düşüş trendinde.",
    ],
    "audience_saturation": [
        "LAL 1% audience reach'inin %{reach_pct}'ine ulaşıldı. Frequency {freq}, CPM {cpm} {currency}'a yükseldi.",
        "Core audience exhausted: estimated reach'in %{reach_pct}'i tüketildi. CPM artıyor, CVR düşüyor.",
    ],
    "roas_decline_gradual": [
        "ROAS son 30 günde kademeli düştü: {roas_30d}x → {roas_14d}x → {roas_7d}x. Spend sabit ama revenue azalıyor.",
        "Gradual ROAS decline: week-over-week %{wow_drop} düşüş 4 haftadır sürüyor. Margin baskı altında.",
    ],
    "margin_negative_roas_ok": [
        "ROAS {roas}x ile hedefin üstünde ama net marj negatif (marj: %{margin}, iade: %{return_rate}, kargo: {shipping} {currency}). Kâğıt üstünde iyi, gerçekte zarar.",
        "Campaign ROAS {roas}x gösteriyor ancak post-return, post-shipping profitability negatif. Gerçek marj %{real_margin}.",
    ],
    "pixel_tracking_broken": [
        "Son {window} günde pixel event'leri %{drop_pct} düştü. Purchase event sayısı platform raporunda {pixel_purchases}, backend'de {backend_purchases}.",
        "Tracking anomaly: conversion event'lerinde ani düşüş. CAPI/server-side events çalışıyor ama browser pixel fire etmiyor.",
    ],
    "attribution_mismatch": [
        "Platform {platform_purchases} purchase raporluyor, Google Analytics {ga_purchases}, backend {backend_purchases}. Hangi rakam doğru?",
        "Attribution window farkı: platform 7d_click ile {p_conv} conversion, 1d_click ile {p_conv_1d}. GA last-click ile {ga_conv}.",
    ],
    "reporting_delay_48h": [
        "Son 48 saatlik veriler eksik/düşük. Platform raporlama gecikmesi şüphesi — gerçek performans belirsiz.",
        "Data lag: 2 gündür conversion data normalin %{lag_pct} altında. Platform status page'de incident bildirimi yok ama delayed reporting söylentisi var.",
    ],
    "platform_outage_suspected": [
        "Bugün tüm campaign'lerde spend durdu / %90 düştü. Platform API yanıt vermiyor. Outage olabilir.",
        "Platform-wide issue: tüm account'larda impression ve spend sıfır. Status page 'investigating' diyor.",
    ],
    "budget_overspend": [
        "Daily budget {budget} {currency} ama gerçekte {actual_spend} {currency} harcanmış. Acceleration veya pacing hatası olabilir.",
        "Budget pacing sorunu: son 3 günde %{overspend_pct} fazla harcama yapıldı.",
    ],
    "budget_underspend": [
        "Daily budget'in sadece %{underspend_pct}'i harcanıyor. Audience çok dar veya bid çok düşük olabilir.",
        "Delivery issue: bütçenin %{underspend_pct}'i harcanıyor. Limited delivery uyarısı var.",
    ],
    "learning_phase_stuck": [
        "Campaign {days_in_learning} gündür learning phase'de — {events}/{target_events} event. Exit stratejisi gerekli.",
        "Learning phase stall: {events} event / {target_events} hedef. Conversion volume yetersiz.",
    ],
    "frequency_too_high": [
        "Frequency {freq} seviyesinde. Ad fatigue belirtileri: CTR düşüyor, negative feedback artıyor.",
        "High frequency alert: {freq}x frequency — audience overlap veya dar targeting olabilir.",
    ],
    "cpm_inflation": [
        "CPM son {window} günde %{cpm_increase} arttı ({cpm_before} → {cpm_after} {currency}). Seasonal/competition etkisi olabilir.",
        "Auction competition artışı: CPM {cpm_before} → {cpm_after}. Competitor spend artmış olabilir.",
    ],
    "low_impression_share": [
        "Impression share sadece %{is_pct}. Lost to rank: %{lost_rank}, lost to budget: %{lost_budget}.",
        "Search impression share %{is_pct} ile çok düşük. Non-brand term'lerde görünürlük yok.",
    ],
    "landing_page_bounce": [
        "Landing page bounce rate %{bounce_rate}. Avg session duration {session_dur}s. Conversion path'de problem var.",
        "Landing page performance düşük: bounce %{bounce_rate}, mobile vs desktop gap: %{mobile_gap}.",
    ],
    "checkout_drop_off": [
        "Add to cart {atc} ama purchase sadece {purchases}. Checkout funnel'da %{dropoff_pct} kayıp. Ödeme/stok/fiyat sorunu olabilir.",
        "Cart abandonment %{abandon_rate}. Initiate checkout'tan purchase'a dönüşüm %{checkout_cvr}.",
    ],
    "stock_out_during_campaign": [
        "Bestseller SKU stokta yok ama reklam hâlâ çalışıyor. Harcama devam ediyor, conversion sıfır.",
        "Stok sorunu: kampanyadaki ana ürün ({product}) tükendi. Reklam bütçesi boşa gidiyor.",
    ],
    "cross_channel_cannibalization": [
        "Meta ve Google aynı kitleye ulaşıyor — overlap tahmini %{overlap_pct}. Toplam CPA artıyor çünkü 2 platform aynı conversion'ı claim ediyor.",
        "Cross-channel cannibalization: Meta retarget + Google retarget same audience. Incrementality testi gerekli.",
    ],
    "video_low_thumbstop": [
        "Thumbstop rate %{thumbstop} — benchmark %25 altında. İlk 2 saniyede hook yeterince dikkat çekmiyor.",
        "Video creative thumbstop %{thumbstop}. Hook testleri gerekli: face-to-camera, text overlay, shock element.",
    ],
    "broad_match_waste": [
        "Broad match keyword'ler toplam spend'in %{broad_pct}'ini yiyor ama CPA {broad_cpa} {currency} (exact CPA: {exact_cpa} {currency}). Search term raporu incelenmeli.",
        "Search term waste: broad match'ten gelen irrelevant term'ler conversion'sız spend'in %{waste_pct}'i.",
    ],
    "feed_disapprovals": [
        "Shopping feed'de {disapproved} ürün disapproved. Feed health %{health}. Top seller'lardan {top_affected} tanesi etkileniyor.",
        "Merchant Center / feed sağlığı düşük: %{health} active. Disapproval sebepleri: {reasons}.",
    ],
    "new_market_cold_start": [
        "Yeni pazar ({market}) açılışı: 0 data, 0 pixel history. Budget {budget} {currency}/gün. Cold start stratejisi gerekli.",
        "Market expansion: {market} pazarına giriş planlı. Benchmark data yok, test bütçesi {budget} {currency}/gün.",
    ],
    "competitor_bid_war": [
        "Son {window} günde CPC %{cpc_increase} arttı. Competitor ({competitor}) aynı keyword'lerde agresif bidding yapıyor.",
        "Auction insights: yeni competitor %{comp_is} impression share almış. CPC'ler yükseliyor.",
    ],
    "wrong_objective_setup": [
        "Kampanya objective'i Traffic ama gerçek hedef satış. Algoritma click optimize ediyor, conversion getirmiyor.",
        "Objective mismatch: campaign awareness/reach optimize ediyor ama KPI conversion. Yanlış setup.",
    ],
    "brand_vs_nonbrand_imbalance": [
        "Search spend'in %{brand_pct}'i brand term'lere gidiyor. Non-brand CPA çok yüksek ({nb_cpa}) — scale edilemiyor.",
        "Brand vs non-brand imbalance: brand ROAS {b_roas}x, non-brand ROAS {nb_roas}x. Brand cannibalizing organic?",
    ],
    "buy_box_lost": [
        "Buy Box oranı %{bb_pct}'a düştü (önceki: %92). {lost_asins} ASIN'de Buy Box kaybedildi. Reklam harcaması verimsiz.",
        "Amazon Buy Box lost: competitor price match + fast shipping ile Buy Box'ı aldı. Sponsored Products click'leri boşa gidiyor.",
    ],
    "seasonal_demand_shift": [
        "Mevsimsel talep değişimi: {season} dönemine girildi. Geçen yılın datası: CPA %{seasonal_delta} {direction}. Bütçe ayarlaması gerekli.",
        "Seasonal shift: {product} kategorisinde arama hacmi %{volume_change} {direction}. Kampanya stratejisi güncellemsi gerekli.",
    ],
    "high_return_rate_hidden": [
        "Platform ROAS {roas}x gösteriyor ama iade oranı %{return_rate}. Gerçek net revenue = {net_revenue} {currency}. Effective ROAS = {effective_roas}x.",
        "Hidden return problem: brüt ROAS iyi ama post-return profitability düşük. Certain creative'ler/audience'lar daha yüksek return rate tetikliyor.",
    ],
    "shipping_cost_eating_margin": [
        "Kargo maliyeti sipariş başına {shipping} {currency}. AOV {aov} {currency}, marj %{margin}. Kargo dahil net marj %{net_margin} — bazı siparişlerde zarar.",
        "Shipping cost erosion: free shipping threshold {threshold} {currency}, avg AOV {aov} {currency}. Alt-threshold siparişler kârsız.",
    ],
    "audience_overlap_waste": [
        "AdSet/AdGroup overlap: {overlap_sets} arası tahmini %{overlap_pct} kitle çakışması. Self-competition var.",
        "Audience overlap: prospecting ve retarget kampanyaları aynı kişilere ulaşıyor — auction inflation + veri kirliliği.",
    ],
    "incrementality_question": [
        "Retarget ROAS {retarget_roas}x ama bu conversions organik olarak da gelir miydi? Incrementality testi gerekli.",
        "Attribution inflated olabilir: last-click %{last_click_pct} retarget'a atanıyor ama brand search zaten artıyor.",
    ],
    "hook_fatigue": [
        "Top performing hook {hook_days} gündür aynı. Thumbstop stable ama CVR %{cvr_drop} düştü. Yeni angle gerekli.",
        "Hook rotation needed: audience hook'a alıştı. View rate stable ama post-click davranış kötüleşiyor.",
    ],
    "price_change_impact": [
        "Ürün fiyatı {old_price} → {new_price} {currency} olarak değişti. CVR {cvr_before}% → {cvr_after}%. Reklam stratejisi güncellenmeli.",
        "Price increase sonrası CVR drop: %{cvr_drop} düşüş. CPA hedefi tutmuyor. Value proposition yeniden çerçevelenmeli.",
    ],
    "capi_event_dedup_issue": [
        "CAPI + Pixel birlikte çalışıyor ama dedup düzgün yapılmamış. Platform {platform_conv} conversion raporluyor, gerçek {real_conv}. Event match quality: {emq}%.",
        "Server-side event dedup hatası: aynı purchase 2x count ediliyor. ROAS şişik görünüyor.",
    ],
    "utm_parameter_missing": [
        "UTM parametreleri eksik/bozuk: GA'da {pct_direct}% trafik 'direct' olarak geliyor. Attribution kırık.",
        "UTM tracking gap: {platform} kampanyalarının %{pct_missing}'inde UTM yok. Cross-channel analiz yapılamıyor.",
    ],
    "data_lag_3_day": [
        "3 günlük data lag: conversion verileri 72 saat gecikmeli geliyor. Gerçek zamanlı optimizasyon imkânsız.",
        "Reporting delay: son 3 günün datası güvenilir değil. Karar vermeden önce data stabilize olmalı.",
    ],
    "video_high_view_low_convert": [
        "Video VTR %{vtr} ile yüksek ama post-view conversion neredeyse sıfır. İzleyenler dönüşmüyor.",
        "Video engagement paradox: avg watch time {watch_time}s, VTR %{vtr} ama CVR %{cvr}. CTA veya landing page problemi.",
    ],
    "roas_spike_then_crash": [
        "ROAS önce {roas_peak}x'e spike yaptı, sonra {roas_now}x'e çöktü. Spike'ın sebebi retarget pool flush veya delayed attribution olabilir.",
        "Volatile ROAS: 3 gün önce {roas_peak}x, bugün {roas_now}x. Sebep araştırması gerekli — gerçek bir dönüşüm değişikliği mi yoksa data artifact mı?",
    ],
}


def _fill_problem_template(
    template: str,
    metrics: dict,
    biz: dict,
    platform: str,
) -> str:
    """Template içindeki placeholder'ları gerçek verilerle doldur."""
    fill = {
        "window": metrics.get("days", 7),
        "cpa_val": metrics.get("cpa", 0),
        "target_cpa": round(metrics.get("cpa", 0) * random.uniform(0.5, 0.85), 2),
        "purchases": metrics.get("purchases", 0),
        "currency": biz["currency"],
        "ctr_before": round(metrics.get("ctr", 1.0) * random.uniform(1.3, 2.0), 2),
        "ctr_after": metrics.get("ctr", 1.0),
        "ctr": metrics.get("ctr", 1.0),
        "ctr_start": round(metrics.get("ctr", 1.0) * random.uniform(1.5, 2.5), 2),
        "drop_pct": random.randint(25, 65),
        "freq": metrics.get("frequency", 2.0),
        "days_active": random.randint(5, 30),
        "reach_pct": random.randint(60, 95),
        "cpm": metrics.get("cpm", 10.0),
        "roas": metrics.get("roas", 1.0),
        "roas_30d": round(metrics.get("roas", 1.0) * random.uniform(1.4, 2.0), 2),
        "roas_14d": round(metrics.get("roas", 1.0) * random.uniform(1.1, 1.5), 2),
        "roas_7d": metrics.get("roas", 1.0),
        "wow_drop": random.randint(5, 20),
        "margin": round(biz["margin_pct"] * 100, 1),
        "return_rate": biz["return_rate_pct"],
        "shipping": biz["shipping_cost"],
        "real_margin": round(biz["margin_pct"] * 100 - biz["return_rate_pct"] - random.uniform(3, 10), 1),
        "pixel_purchases": metrics.get("purchases", 0),
        "backend_purchases": int(metrics.get("purchases", 0) * random.uniform(1.1, 1.8)),
        "platform_purchases": metrics.get("purchases", 0),
        "ga_purchases": int(metrics.get("purchases", 0) * random.uniform(0.6, 0.9)),
        "ga_conv": int(metrics.get("purchases", 0) * random.uniform(0.5, 0.85)),
        "p_conv": metrics.get("purchases", 0),
        "p_conv_1d": int(metrics.get("purchases", 0) * random.uniform(0.4, 0.7)),
        "lag_pct": random.randint(40, 80),
        "budget": round(random.uniform(50, 2000), 0),
        "actual_spend": round(random.uniform(50, 2000) * random.uniform(1.1, 1.5), 2),
        "overspend_pct": random.randint(10, 50),
        "underspend_pct": random.randint(15, 60),
        "days_in_learning": random.randint(4, 14),
        "events": random.randint(5, 35),
        "target_events": random.choice([30, 50]),
        "cpm_before": round(metrics.get("cpm", 10.0) * random.uniform(0.5, 0.8), 2),
        "cpm_after": metrics.get("cpm", 10.0),
        "cpm_increase": random.randint(15, 80),
        "is_pct": random.randint(8, 35),
        "lost_rank": random.randint(20, 55),
        "lost_budget": random.randint(15, 45),
        "bounce_rate": random.randint(55, 90),
        "session_dur": round(random.uniform(8, 45), 1),
        "mobile_gap": random.randint(10, 35),
        "atc": metrics.get("add_to_cart", 0),
        "dropoff_pct": random.randint(40, 80),
        "abandon_rate": random.randint(55, 85),
        "checkout_cvr": round(random.uniform(10, 45), 1),
        "product": biz["product_name"],
        "overlap_pct": random.randint(20, 65),
        "overlap_sets": random.choice(["AdSet A ve B", "Campaign 1 ve 3", "AdGroup Alpha ve Beta"]),
        "thumbstop": round(random.uniform(8, 22), 1),
        "broad_pct": random.randint(40, 75),
        "broad_cpa": round(metrics.get("cpa", 10) * random.uniform(1.3, 2.5), 2),
        "exact_cpa": round(metrics.get("cpa", 10) * random.uniform(0.5, 0.9), 2),
        "waste_pct": random.randint(20, 55),
        "disapproved": random.randint(5, 80),
        "health": random.randint(65, 92),
        "top_affected": random.randint(2, 10),
        "reasons": random.choice(["image quality + missing GTIN", "price mismatch + policy violation", "shipping info + product type error"]),
        "market": random.choice(["Almanya", "Suudi Arabistan", "Japonya", "Brezilya", "Hindistan"]),
        "competitor": random.choice(["CompetitorX", "BrandY", "RivalZ"]),
        "comp_is": random.randint(8, 30),
        "cpc_increase": random.randint(15, 60),
        "brand_pct": random.randint(55, 85),
        "nb_cpa": round(metrics.get("cpa", 10) * random.uniform(2.0, 4.0), 2),
        "b_roas": round(random.uniform(5.0, 15.0), 1),
        "nb_roas": round(random.uniform(0.5, 2.5), 1),
        "bb_pct": random.randint(50, 80),
        "lost_asins": random.randint(3, 15),
        "season": random.choice(["yaz", "kış", "bahar", "Black Friday", "Bayram", "Back-to-School"]),
        "seasonal_delta": random.randint(10, 40),
        "direction": random.choice(["artış", "düşüş"]),
        "volume_change": random.randint(15, 60),
        "net_revenue": round(metrics.get("revenue", 0) * (1 - biz.get("return_rate_pct", 10) / 100), 2),
        "effective_roas": round(metrics.get("roas", 1.0) * (1 - biz.get("return_rate_pct", 10) / 100), 2),
        "aov": metrics.get("aov", 50),
        "net_margin": round(biz["margin_pct"] * 100 - biz.get("return_rate_pct", 10) - biz["shipping_cost"] / max(metrics.get("aov", 50), 1) * 100, 1),
        "threshold": round(random.uniform(30, 100), 0),
        "retarget_roas": round(random.uniform(4.0, 12.0), 1),
        "last_click_pct": random.randint(55, 85),
        "hook_days": random.randint(7, 25),
        "cvr_drop": random.randint(15, 45),
        "old_price": round(biz["price"] * random.uniform(0.7, 0.95), 2),
        "new_price": biz["price"],
        "cvr_before": round(random.uniform(1.5, 5.0), 2),
        "cvr_after": round(random.uniform(0.5, 2.0), 2),
        "platform_conv": int(metrics.get("purchases", 0) * random.uniform(1.3, 2.0)),
        "real_conv": metrics.get("purchases", 0),
        "emq": random.randint(40, 85),
        "pct_direct": random.randint(20, 55),
        "pct_missing": random.randint(30, 70),
        "vtr": round(random.uniform(15, 45), 1),
        "watch_time": round(random.uniform(5, 18), 1),
        "cvr": round(random.uniform(0.1, 0.8), 2),
        "roas_peak": round(random.uniform(4.0, 10.0), 1),
        "roas_now": round(random.uniform(0.5, 2.0), 1),
    }

    try:
        return template.format(**fill)
    except KeyError:
        # Fallback — sadece bilinen key'leri doldur
        import re
        def _safe_replace(m):
            key = m.group(1)
            return str(fill.get(key, m.group(0)))
        return re.sub(r"\{(\w+)\}", _safe_replace, template)


def pick_problem_and_statement(
    metrics: dict,
    biz: dict,
    platform: str,
    problem_type: str | None = None,
) -> tuple[str, str]:
    """Rastgele veya belirtilen problem tipini seç ve cümlesini üret."""
    if problem_type is None:
        problem_type = random.choice(C.PROBLEM_TYPES)

    templates = _PROBLEM_TEMPLATES.get(problem_type)
    if not templates:
        # Fallback: generic
        templates = _PROBLEM_TEMPLATES.get("high_cpa_low_conversions", ["Performans problemi mevcut."])

    template = random.choice(templates)
    statement = _fill_problem_template(template, metrics, biz, platform)
    return problem_type, statement


# ──────────────────────────────────────────────
# BREAKDOWN GENERATOR
# ──────────────────────────────────────────────

def generate_breakdown(platform: str, n: int = 3) -> list[dict]:
    """Kampanya/adgroup/creative breakdown üretir."""
    breakdown = []
    for i in range(n):
        name = P.generate_adgroup_name(platform) if random.random() > 0.4 else P.generate_ad_name()
        mini_metrics = S.generate_coherent_metrics(
            **P.get_metric_ranges(platform),
            days=random.choice([3, 7]),
        )
        breakdown.append({
            "entity": name,
            "spend": mini_metrics["spend"],
            "impressions": mini_metrics["impressions"],
            "clicks": mini_metrics["clicks"],
            "ctr": mini_metrics["ctr"],
            "purchases": mini_metrics["purchases"],
            "cpa": mini_metrics["cpa"],
            "roas": mini_metrics["roas"],
        })
    return breakdown


# ──────────────────────────────────────────────
# TRACKING / ATTRIBUTION CONTEXT
# ──────────────────────────────────────────────

def generate_tracking_context(platform: str) -> str:
    """Tracking / attribution bağlam cümlesi üret."""
    templates = [
        "Pixel + CAPI aktif, event match quality %{emq}. Attribution window: {attr_win}.",
        "Sadece browser pixel kullanılıyor — CAPI henüz kurulmadı. iOS traffic'in %{ios_pct}'i signal loss.",
        "Server-side tracking aktif. Dedup çalışıyor. Reporting delay: ~{delay}h.",
        "GTM ile pixel fire ediliyor. CAPI yok. UTM parametreleri {utm_status}.",
        "Pixel + CAPI dual setup. Event match quality: %{emq}. Son 7 günde {pixel_events} pixel event, {capi_events} CAPI event.",
    ]
    template = random.choice(templates)
    fill = {
        "emq": random.randint(40, 95),
        "attr_win": P.pick_attribution_window(platform),
        "ios_pct": random.randint(25, 55),
        "delay": random.choice([2, 4, 8, 24, 48]),
        "utm_status": random.choice(["düzgün", "eksik", "kısmen bozuk"]),
        "pixel_events": random.randint(50, 500),
        "capi_events": random.randint(40, 480),
    }
    return template.format(**fill)


# ──────────────────────────────────────────────
# FULL SCENARIO BUILDER
# ──────────────────────────────────────────────

def build_scenario(
    platform: str,
    task_type: str,
    example_id: str,
    *,
    force_problem: str | None = None,
    force_flags: dict | None = None,
) -> dict:
    """
    Tam bir senaryo oluşturur: business context + metrics + problem + breakdown + tracking.
    Dönen dict doğrudan JSONL satırına yazılacak formatta.
    """
    flags = force_flags or {}

    # Determine special scenario flags
    is_low_spend      = flags.get("low_spend", random.random() < C.LOW_SPEND_GUARDRAIL_RATIO)
    is_negative_margin = flags.get("negative_margin", random.random() < C.NEGATIVE_MARGIN_RATIO)
    is_misleading      = flags.get("misleading", random.random() < C.MISLEADING_CORRELATION_RATIO)
    is_outage          = flags.get("outage", random.random() < C.PLATFORM_OUTAGE_RATIO)

    # Business context
    biz = _pick_business_context()

    # Metrics
    ranges = P.get_metric_ranges(platform)
    days = random.choice(C.TIME_WINDOWS)
    metrics = S.generate_coherent_metrics(
        **ranges,
        days=days,
        low_spend=is_low_spend,
        negative_margin=is_negative_margin,
        margin_pct=biz["margin_pct"],
    )

    # Problem type selection  — special cases override
    if is_outage:
        force_problem = random.choice(["reporting_delay_48h", "platform_outage_suspected", "data_lag_3_day"])
    elif is_misleading:
        force_problem = random.choice([
            "checkout_drop_off", "stock_out_during_campaign", "price_change_impact",
            "high_return_rate_hidden", "shipping_cost_eating_margin",
            "margin_negative_roas_ok",
        ])
    elif is_negative_margin:
        force_problem = force_problem or "margin_negative_roas_ok"

    problem_type, problem_statement = pick_problem_and_statement(
        metrics, biz, platform, force_problem,
    )

    # Platform-specific elements
    plat_elements = P.get_platform_scenario_elements(platform)

    # Breakdown
    breakdown = generate_breakdown(platform, n=random.randint(2, 5))

    # Tracking
    tracking = generate_tracking_context(platform)

    # Campaign name
    campaign_name = P.generate_campaign_name()

    # Time series (optional — 60% of scenarios)
    time_series = None
    if random.random() < 0.60:
        trend = random.choice(["declining", "improving", "stable", "volatile"])
        time_series = S.generate_time_series(metrics, windows=[3, 7, 14], trend=trend)

    # ── Assemble user prompt ──
    user_prompt = _build_user_prompt(
        task_type=task_type,
        platform=platform,
        biz=biz,
        metrics=metrics,
        problem_type=problem_type,
        problem_statement=problem_statement,
        plat_elements=plat_elements,
        breakdown=breakdown,
        tracking=tracking,
        campaign_name=campaign_name,
        time_series=time_series,
        is_low_spend=is_low_spend,
        is_negative_margin=is_negative_margin,
    )

    # ── Tags ──
    tags = [task_type, platform, biz["industry"], biz["country_code"], problem_type]
    if is_low_spend:
        tags.append("low_spend_guardrail")
    if is_negative_margin:
        tags.append("negative_margin")
    if is_misleading:
        tags.append("misleading_correlation")
    if is_outage:
        tags.append("outage_delay")

    return {
        "id": example_id,
        "platform": platform,
        "task_type": task_type,
        "language": "tr",
        "system": C.TEACHER_SYSTEM_PROMPT,
        "user": user_prompt,
        "schema_hint": C.SCHEMA_HINT,
        "tags": tags,
    }


def _build_user_prompt(
    *,
    task_type: str,
    platform: str,
    biz: dict,
    metrics: dict,
    problem_type: str,
    problem_statement: str,
    plat_elements: dict,
    breakdown: list[dict],
    tracking: str,
    campaign_name: str,
    time_series: dict | None,
    is_low_spend: bool,
    is_negative_margin: bool,
) -> str:
    """Tüm bileşenleri birleştirip user promptunu oluşturur."""
    lines = []

    # Header
    lines.append(f"## {task_type} — {P.get_platform_config(platform)['display_name']}")
    lines.append("")

    # Business context
    lines.append("### İş Bağlamı")
    lines.append(f"- Sektör: {biz['industry']}")
    lines.append(f"- Ürün: {biz['product_name']}")
    lines.append(f"- Fiyat: {biz['price']} {biz['currency']}")
    lines.append(f"- Marj: %{round(biz['margin_pct'] * 100, 1)}")
    lines.append(f"- İade oranı: %{biz['return_rate_pct']}")
    lines.append(f"- Kargo maliyeti: {biz['shipping_cost']} {biz['currency']}")
    lines.append(f"- Ülke: {biz['country']} ({biz['country_code']})")
    lines.append(f"- Stok durumu: {biz['stock_status']}")
    lines.append(f"- Hedef KPI: {biz['target_kpi']}")
    lines.append("")

    # Campaign info
    lines.append(f"### Kampanya: {campaign_name}")

    # Platform specific elements
    for k, v in plat_elements.items():
        if k != "platform" and isinstance(v, str):
            lines.append(f"- {k}: {v}")
    lines.append("")

    # Metrics
    lines.append(f"### Metrikler (son {metrics['days']} gün)")
    lines.append(f"- Spend: {metrics['spend']} {biz['currency']}")
    lines.append(f"- Impressions: {metrics['impressions']:,}")
    lines.append(f"- Reach: {metrics['reach']:,} | Frequency: {metrics['frequency']}")
    lines.append(f"- Clicks: {metrics['clicks']:,} | CTR: %{metrics['ctr']} | CPC: {metrics['cpc']} {biz['currency']}")
    lines.append(f"- CPM: {metrics['cpm']} {biz['currency']}")
    lines.append(f"- Add to Cart: {metrics['add_to_cart']} | Initiate Checkout: {metrics['initiate_checkout']}")
    lines.append(f"- Purchases: {metrics['purchases']} | CVR: %{metrics['cvr']} | CPA: {metrics['cpa']} {biz['currency']}")
    lines.append(f"- Revenue: {metrics['revenue']} {biz['currency']} | AOV: {metrics['aov']} {biz['currency']}")
    lines.append(f"- ROAS: {metrics['roas']}x")
    lines.append(f"- Tahmini Marj: %{metrics['margin_pct']} | Tahmini Kâr: {metrics['profit_est']} {biz['currency']}")
    lines.append("")

    # Time series (if available)
    if time_series:
        lines.append("### Trend Karşılaştırması")
        for window_key, ts_metrics in time_series.items():
            d = ts_metrics["days"]
            lines.append(f"- {window_key}: spend={ts_metrics['spend']}, ROAS={ts_metrics.get('roas', 'N/A')}x, CPA={ts_metrics.get('cpa', 'N/A')}, CTR=%{ts_metrics.get('ctr', 'N/A')}")
        lines.append("")

    # Breakdown
    lines.append("### Breakdown")
    for b in breakdown:
        lines.append(f"- {b['entity']}: spend={b['spend']}, clicks={b['clicks']}, CTR=%{b['ctr']}, purchases={b['purchases']}, CPA={b['cpa']}, ROAS={b['roas']}x")
    lines.append("")

    # Tracking
    lines.append(f"### Tracking / Attribution")
    lines.append(f"- {tracking}")
    lines.append("")

    # Problem statement
    lines.append("### Sorun")
    lines.append(problem_statement)
    lines.append("")

    # Guardrails reminder
    lines.append("### Guardrails")
    lines.append("- Aynı gün bütçe değişimi max %25")
    if is_low_spend:
        lines.append("- ⚠️ LOW SPEND: Son 3 günde spend < 30 — agresif karar verme, ölçüm/deney öner")
    if is_negative_margin:
        lines.append("- ⚠️ MARJ NEGATİF: ROAS iyi görünse bile kâr odaklı aksiyon üret")
    lines.append("- Learning phase reset etme (gerekmedikçe)")
    lines.append("")

    # Requested output
    lines.append(f"### İstenen Çıktı")
    lines.append(f"Görev tipi: {task_type}")
    lines.append(f"Platform: {platform}")
    lines.append("Sadece JSON formatında yanıtla. Metin açıklama ekleme.")

    return "\n".join(lines)
