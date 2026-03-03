"""
convert_tabular_datasets.py
============================
Anlamli kolonlara sahip tum tablosal Kaggle datasetlerini indirir
ve Qwen3-VL Thinking formatina donusturur.

Her satir: {kampanya/musteri verisi} → {analiz + aksiyon onerileri}

Kullanim:
    python scripts/convert_tabular_datasets.py
    python scripts/convert_tabular_datasets.py --output /workspace/models/tmp/tabular_data.jsonl
"""

import os, sys, json, csv, argparse, glob, random
from pathlib import Path
from tqdm import tqdm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KAGGLE_DATA_DIR = "/workspace/data/tabular"
OUTPUT_FILE     = "/workspace/models/tmp/tabular_data.jsonl"

SYSTEM_PROMPT = """Sen bir satis psikolojisi ve dijital reklam stratejisi uzmanisın.
Kampanya verilerini analiz eder, benchmark karsilastirmasi yapar ve
somut optimizasyon onerileri sunarsın."""


# ─────────────────────────────────────────────────────────────────────────────
# Yardimci fonksiyonlar
# ─────────────────────────────────────────────────────────────────────────────

def safe(val, default="Bilinmiyor") -> str:
    if val is None or str(val).strip() in ("", "nan", "NaN", "None"):
        return default
    return str(val).strip()

def pct(val, benchmark, label="") -> str:
    """Benchmark ile karsilastir, yorumla."""
    try:
        v = float(val)
        b = float(benchmark)
        diff = (v - b) / b * 100
        if diff > 20:
            return f"{v:.2f} (YUKSEK — benchmark {b:.2f}'nin %{diff:.0f} ustunde)"
        elif diff < -20:
            return f"{v:.2f} (DUSUK — benchmark {b:.2f}'nin %{abs(diff):.0f} altinda)"
        else:
            return f"{v:.2f} (NORMAL — benchmark: {b:.2f})"
    except (ValueError, TypeError, ZeroDivisionError):
        return safe(val)

def think(instruction: str, insight: str) -> str:
    preview = instruction[:150].replace("\n", " ")
    return (
        f"<think>\n"
        f"Veriyi inceliyorum: {preview}\n"
        f"Benchmark karsilastirmasi ve aksiyon onerileri hazirliyorum.\n"
        f"</think>\n\n"
        f"{insight}"
    )

def make_ex(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": user[:4000]},
            {"role": "assistant", "content": think(user, assistant[:4000])},
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# CONVERTER'LAR
# ─────────────────────────────────────────────────────────────────────────────

def convert_facebook_ad(row: dict):
    """madislemsalu/facebook-ad-campaign"""
    impressions = safe(row.get("Impressions", row.get("impressions", "")))
    clicks      = safe(row.get("Clicks", row.get("clicks", row.get("Total_clicks", ""))))
    spend       = safe(row.get("Spent", row.get("spend", row.get("Amount_spent_(USD)", ""))))
    conversions = safe(row.get("Total_Conversion", row.get("conversions", "")))
    age         = safe(row.get("age", row.get("Age", "")))
    gender      = safe(row.get("gender", row.get("Gender", "")))
    interest    = safe(row.get("interest", row.get("Interest", "")))

    if impressions == "Bilinmiyor" and clicks == "Bilinmiyor":
        return None

    try:
        ctr  = float(clicks) / float(impressions) * 100 if float(impressions) > 0 else 0
        cpc  = float(spend)  / float(clicks) if float(clicks) > 0 else 0
        conv = float(conversions) / float(clicks) * 100 if float(clicks) > 0 else 0
        ctr_str  = pct(ctr, 1.9, "CTR")
        cpc_str  = f"${cpc:.2f} ({'YUKSEK — rekabetci segment' if cpc > 2.5 else 'MAKUL'})"
        conv_str = pct(conv, 2.5, "CVR")
    except (ValueError, TypeError):
        ctr_str = f"Impr:{impressions} Clicks:{clicks}"
        cpc_str = f"Spend:{spend}"
        conv_str = f"Conv:{conversions}"

    user_msg = (
        f"Bu Facebook reklam kampanyasını analiz et:\n\n"
        f"Hedef kitle: {age} yas, {gender}, Ilgi alani: {interest}\n"
        f"Gosterim: {impressions} | Tiklanma: {clicks} | Harcama: ${spend}\n"
        f"Donusum: {conversions}\n\n"
        f"CTR, CPC ve donusum oranlari ne duruyor? Optimizasyon onerileri neler?"
    )
    response = (
        f"Facebook Reklam Analizi\n\n"
        f"CTR: {ctr_str}\n"
        f"CPC: {cpc_str}\n"
        f"Donusum Orani: {conv_str}\n\n"
        f"Hedef Kitle Değerlendirmesi:\n"
        f"- {age} yas, {gender} segmenti bu sonuclari uretmis\n"
        f"- Ilgi alani '{interest}' hedeflemesi {'etkin gorunuyor' if ctr_str and 'NORMAL' in ctr_str or 'YUKSEK' in ctr_str else 'iyilestirilmeli'}\n\n"
        f"Aksiyon Onerileri:\n"
        f"1. {'CTR dusukse kreatif gorseli degistir, ilk 3 saniye dikkat cekici olmali' if 'DUSUK' in ctr_str else 'CTR iyi, benzer kreatifleri diger segmentlere yay'}\n"
        f"2. {'CPC yuksekse hedef kitleyi daralt, LAL (Lookalike) audience dene' if 'YUKSEK' in cpc_str else 'CPC makul seviyede, butceyi artirabilirsin'}\n"
        f"3. {'Donusum dusukse landing page A/B test et, form/CTA basitlestir' if 'DUSUK' in conv_str else 'Donusum orani iyi, retargeting ile takviye et'}\n"
        f"4. Farkli yas gruplarini ayri ad set'lerde test et — {age} disinda 25-44 segmentini dene"
    )
    return make_ex(user_msg, response)


def convert_marketing_perf(row: dict):
    """manishabhatt22/marketing-campaign-performance-dataset"""
    channel    = safe(row.get("Channel", row.get("Channel_Used", row.get("channel", ""))))
    campaign   = safe(row.get("Campaign_Type", row.get("Type", row.get("campaign_type", ""))))
    spend      = safe(row.get("Budget", row.get("Spend", row.get("spend", ""))))
    revenue    = safe(row.get("Revenue", row.get("revenue", "")))
    ctr        = safe(row.get("CTR", row.get("ctr", "")))
    conv_rate  = safe(row.get("Conversion_Rate", row.get("conversion_rate", "")))
    roi        = safe(row.get("ROI", row.get("roi", "")))

    if channel == "Bilinmiyor" and campaign == "Bilinmiyor":
        return None

    try:
        roi_val = float(roi)
        roi_status = "POZITIF" if roi_val > 0 else "NEGATIF"
    except (ValueError, TypeError):
        roi_status = "belirsiz"

    user_msg = (
        f"Bu pazarlama kampanyasini analiz et ve stratejik oneriler sun:\n\n"
        f"Kanal: {channel} | Kampanya Turu: {campaign}\n"
        f"Butce: {spend} | Gelir: {revenue} | ROI: {roi}\n"
        f"CTR: {ctr} | Donusum Orani: {conv_rate}\n\n"
        f"Performans degerlendirmesi ve iyilestirme onerileri neler?"
    )
    response = (
        f"Kampanya Performans Analizi\n\n"
        f"Kanal: {channel} — {campaign} kampanyasi\n"
        f"Mali Sonuc: ROI {roi} ({roi_status})\n\n"
        f"Metrik Degerlendirmesi:\n"
        f"- CTR {ctr}: {'Sektör ortalama %1.9 ile karsilastirinca' if ctr != 'Bilinmiyor' else 'Veri yok'}\n"
        f"- Donusum {conv_rate}: {'Benchmark %2.5 ile karsilastirinca' if conv_rate != 'Bilinmiyor' else 'Veri yok'}\n\n"
        f"Optimizasyon Onerileri ({channel} icin):\n"
        f"1. En yuksek ROI getiren audience segmentini izole et ve butceyi ona kaydir\n"
        f"2. {'Dijital kanallar icin: Bid strategy otomatik olarak tROAS moduna al' if channel in ['Google', 'Meta', 'Digital', 'Online'] else 'Kanal mix optimizasyonu: Diger kanallari A/B test et'}\n"
        f"3. ROI {roi_status} oldugu icin {'harcamayi durdur, stratejiyi gozden gecir' if roi_status == 'NEGATIF' else 'basarili segmente butce artir'}\n"
        f"4. Aylik butce revizyonu: Harcama-ROI korrelasyonunu haftalik takip et"
    )
    return make_ex(user_msg, response)


def convert_consumer_behavior(row: dict):
    """zeesolver/consumer-behavior-and-shopping-habits-dataset"""
    age         = safe(row.get("Age", ""))
    gender      = safe(row.get("Gender", ""))
    purchase_amt= safe(row.get("Purchase Amount (USD)", row.get("Purchase_Amount", "")))
    category    = safe(row.get("Category", row.get("Item Purchased", "")))
    freq        = safe(row.get("Frequency of Purchases", row.get("Purchase_Frequency", "")))
    discount    = safe(row.get("Discount Applied", row.get("Promo_Code_Used", "")))
    payment     = safe(row.get("Payment Method", row.get("Payment_Method", "")))

    if age == "Bilinmiyor" and purchase_amt == "Bilinmiyor":
        return None

    user_msg = (
        f"Bu musteri profilini analiz et. Hangi segmente giriyor? Hangi satis stratejisi uygulanmali?\n\n"
        f"Yas: {age} | Cinsiyet: {gender}\n"
        f"Kategori: {category} | Harcama: ${purchase_amt}\n"
        f"Satin Alma Sikligi: {freq}\n"
        f"Promosyon Kullanimi: {discount} | Odeme: {payment}"
    )
    response = (
        f"Musteri Segmentasyon Analizi\n\n"
        f"Profil: {age} yas, {gender} musteri\n"
        f"Segment: {'Premium' if float(purchase_amt or 0) > 100 else 'Standart' if float(purchase_amt or 0) > 50 else 'Ekonomi'} alici\n\n"
        f"Davranis Analizi:\n"
        f"- {freq} satin alma sikligi: {'Sadik musteri — loyalty program icin ideal aday' if freq in ['Weekly', 'Bi-Weekly', 'Fortnightly'] else 'Ara sira alisveris — reaktivasyon kampanyasi gerekli'}\n"
        f"- Promosyon: {discount} — {'Promosyona duyarli, indirim odakli segmente al' if str(discount).lower() in ['yes','true','1'] else 'Promosyona bagımlı degil, urun kalitesi on planda'}\n"
        f"- Odeme: {payment} — {'Dijital odeme = tekrar alisverise hazir' if payment in ['Credit Card', 'PayPal', 'Venmo'] else 'Nakit odeme = daha ihtiyatli musteri'}\n\n"
        f"Satis Stratejisi:\n"
        f"1. Upsell: {category} kategorisinde premium alternatifleri oner\n"
        f"2. Cross-sell: Tamamlayici urun kategorilerini otomatik oner\n"
        f"3. Email segmenti: {freq} satin alma ritminde hatirlatici gonder\n"
        f"4. {'Loyalty puani ver - bu musteri uzun vadeli deger tasıyor' if freq in ['Weekly', 'Bi-Weekly'] else 'Win-back kampanyasi: 30 gun sonra otomatik indirim emaili'}"
    )
    return make_ex(user_msg, response)


def convert_ecommerce_behavior(row: dict):
    """uom190346a/e-commerce-customer-behavior-dataset"""
    age           = safe(row.get("Age", ""))
    gender        = safe(row.get("Gender", ""))
    total_spend   = safe(row.get("Total Spend", row.get("Total_Spend", "")))
    items         = safe(row.get("Items Purchased", row.get("Items_Purchased", "")))
    avg_rating    = safe(row.get("Average Rating", row.get("Avg_Rating", "")))
    membership    = safe(row.get("Membership Type", row.get("Membership", "")))
    satisfaction  = safe(row.get("Satisfaction Level", row.get("Satisfaction", "")))

    if age == "Bilinmiyor" and total_spend == "Bilinmiyor":
        return None

    try:
        avg_order = float(total_spend) / float(items) if float(items) > 0 else 0
        aov_str = f"${avg_order:.2f} ortalama siparis degeri"
    except (ValueError, TypeError):
        aov_str = f"Harcama: {total_spend}"

    user_msg = (
        f"Bu e-ticaret musterisinin CLV (musteri yasam boyu degeri) ve churn riski nedir?\n\n"
        f"Yas: {age} | Cinsiyet: {gender} | Uyelik: {membership}\n"
        f"Toplam Harcama: ${total_spend} | Satin Alinan Urun: {items}\n"
        f"Ortalama Puan: {avg_rating}/5 | Memnuniyet: {satisfaction}"
    )
    response = (
        f"E-Ticaret Musteri Analizi\n\n"
        f"CLV Tahmini: {aov_str}\n"
        f"Uyelik Seviyesi: {membership}\n\n"
        f"Churn Risk Degerlendirmesi:\n"
        f"- Memnuniyet '{satisfaction}': {'DUSUK churn riski — musteri memnun' if str(satisfaction).lower() in ['satisfied', 'high', 'very satisfied'] else 'YUKSEK churn riski — acil mudahale gerekli'}\n"
        f"- Puan {avg_rating}/5: {'Pozitif deneyim, referral potansiyeli yuksek' if float(avg_rating or 0) >= 4 else 'Deneyim iyilestirilmeli'}\n"
        f"- {membership} uye: {'Premium uye — ozel teklif sunulmali' if 'gold' in str(membership).lower() or 'premium' in str(membership).lower() else 'Uyelik upgrade kampanyası gonder'}\n\n"
        f"CRM Aksiyonlari:\n"
        f"1. {'VIP musteri programina davet et' if float(total_spend or 0) > 500 else 'Loyalty puan kampanyasiyla harcamayi artir'}\n"
        f"2. {'NPS anketi gonder — potansiyel brand ambassador' if float(avg_rating or 0) >= 4 else 'Memnuniyet anketi + iyziyat teklifi gonder'}\n"
        f"3. Kisisellestirilmis urun onerileri: {items} urun satin almis, benzer kategorileri oner\n"
        f"4. {membership} uyelik kitleyici teklif: Bir ust seviyeye gecis icin indirim ver"
    )
    return make_ex(user_msg, response)


def convert_online_retail(row: dict):
    """UCI Online Retail Dataset"""
    invoice     = safe(row.get("InvoiceNo", ""))
    stock       = safe(row.get("StockCode", ""))
    description = safe(row.get("Description", ""))
    quantity    = safe(row.get("Quantity", ""))
    unit_price  = safe(row.get("UnitPrice", ""))
    country     = safe(row.get("Country", ""))

    if description == "Bilinmiyor" or quantity == "Bilinmiyor":
        return None

    try:
        revenue = float(quantity) * float(unit_price)
        rev_str = f"${revenue:.2f}"
    except (ValueError, TypeError):
        rev_str = "Hesaplanamadi"

    user_msg = (
        f"Bu perakende satis verisini analiz et:\n\n"
        f"Urun: {description}\n"
        f"Miktar: {quantity} adet @ £{unit_price}\n"
        f"Toplam: {rev_str} | Ulke: {country}\n\n"
        f"Bu urun icin satis stratejisi ve upsell onerileri?"
    )
    response = (
        f"Perakende Satis Analizi\n\n"
        f"Urun: {description}\n"
        f"Birim Gelir: {rev_str} ({quantity} adet)\n"
        f"Pazar: {country}\n\n"
        f"Stratejik Degerendirme:\n"
        f"- {'Yuksek adetli siparis — B2B musteri olabilir, kurumsal fiyatlandirma sun' if float(quantity or 0) > 50 else 'Bireysel satin alim — retail fiyatlandirma geçerli'}\n"
        f"- {country} pazari: {'UK i pazari icin yerel odeme yontemleri ve hizli kargo on planda' if country == 'United Kingdom' else f'{country} icin ulkesine ozel promosyon ve kargo secenegi sun'}\n\n"
        f"Upsell / Cross-sell:\n"
        f"1. {description} alanlar genellikle tamamlayici aksesuarlar da aliyor — bundle teklif olustur\n"
        f"2. Ayni musteriye {quantity} adet uzerinde indirim sun — hacim indirimi ile siparis buyuklugunu artir\n"
        f"3. Tekrar satin alma hatirlatmasi: {description} icin yenileme/yedek stok maili gonder"
    )
    return make_ex(user_msg, response)


def convert_ab_test_full(row: dict):
    """faviovaz/marketing-ab-testing"""
    user_id   = safe(row.get("user id", row.get("user_id", "")))
    group     = safe(row.get("test group", row.get("group", "")))
    converted = safe(row.get("converted", ""))
    total_ads = safe(row.get("total ads", row.get("ads", "")))
    peak_day  = safe(row.get("most ads day", row.get("peak_day", "")))
    peak_hour = safe(row.get("most ads hour", row.get("peak_hour", "")))

    if group == "Bilinmiyor":
        return None

    user_msg = (
        f"A/B test sonucunu yorumla ve istatistiksel anlamlilik degerlendirmesi yap:\n\n"
        f"Kullanici Grubu: {group}\n"
        f"Donusum: {converted}\n"
        f"Gorulen Reklam Sayisi: {total_ads}\n"
        f"En Yogun Gun: {peak_day} | En Yogun Saat: {peak_hour}:00\n\n"
        f"Bu verilere gore kampanya optimizasyonu nasil yapilmali?"
    )
    response = (
        f"A/B Test Analizi\n\n"
        f"Grup: {group} | Donusum: {converted}\n\n"
        f"Frekans Analizi:\n"
        f"- {total_ads} reklam goruntulemesi: {'Fazla maruz kalma — reklam yorgunlugu riski' if float(total_ads or 0) > 20 else 'Makul frekans — optimal goruntusu'}\n"
        f"- En iyi performans: {peak_day} gunu, saat {peak_hour}:00\n\n"
        f"Optimizasyon Onerileri:\n"
        f"1. Reklam zamanlamasi: {peak_day} gunleri saat {peak_hour}:00 civarinda butceyi %30 artir\n"
        f"2. {'Ad grubu kazaniyor — butceyi ad grubuna kaydir' if group == 'ad' and str(converted).lower() == 'true' else 'Kontrol grubunda donusum var — organik icerik guclendirilebilir'}\n"
        f"3. Frekans siniri koy: Kullanici basina maksimum 10-15 gosterim — sonrasinda farkli kreatif don\n"
        f"4. Saat bazli bid adjustment: {peak_hour}:00 saatinde bid'i %20-40 yuksel"
    )
    return make_ex(user_msg, response)


def convert_churn_full(row: dict):
    """blastchar/telco-customer-churn + varyantlar"""
    tenure       = safe(row.get("tenure", ""))
    monthly      = safe(row.get("MonthlyCharges", row.get("Monthly_Charges", "")))
    total_charge = safe(row.get("TotalCharges", row.get("Total_Charges", "")))
    contract     = safe(row.get("Contract", row.get("contract", "")))
    internet     = safe(row.get("InternetService", row.get("Internet_Service", "")))
    churn        = safe(row.get("Churn", row.get("churn", "")))
    tech_support = safe(row.get("TechSupport", row.get("tech_support", "")))
    payment      = safe(row.get("PaymentMethod", row.get("Payment_Method", "")))

    if churn == "Bilinmiyor":
        return None

    churn_bool = str(churn).lower() in ["yes", "1", "true", "churn"]

    user_msg = (
        f"Bu telekom musterisinin churn riskini degerlendir ve satis/retansiyon stratejisi sun:\n\n"
        f"Abonelik Suresi: {tenure} ay | Aylik Ucret: ${monthly}\n"
        f"Sozlesme Turu: {contract} | Internet: {internet}\n"
        f"Teknik Destek: {tech_support} | Odeme: {payment}\n"
        f"Churn: {churn}"
    )
    response = (
        f"Churn Analizi ve Retansiyon Stratejisi\n\n"
        f"Musteri Durumu: {'CHURN ETTI' if churn_bool else 'AKTIF'}\n"
        f"Risk Seviyesi: {'KRITIK' if churn_bool else ('YUKSEK' if contract == 'Month-to-month' else 'DUSUK')}\n\n"
        f"Neden Churn Etti/Edebilir:\n"
        f"- Sozlesme: {contract} — {'Month-to-month = en yuksek churn riski, baglamayi dogrudan onlemez' if contract == 'Month-to-month' else 'Yillik sozlesme = daha stable'}\n"
        f"- Sure: {tenure} ay — {'Yeni musteri, henuz baglilik olusturmamis' if float(tenure or 0) < 12 else 'Uzun sureli musteri, ama tatminsiz olabilir'}\n"
        f"- Teknik destek: {tech_support} — {'Destek yok = sorun cozulemeyince churn' if tech_support in ['No', 'No internet service'] else 'Destekten memnun olmayabilir'}\n\n"
        f"{'GERİ KAZANMA' if churn_bool else 'RETANSIYON'} Stratejisi:\n"
        f"1. {'Kisisel arama + ozel indirim teklifi: 3 aylik ucret kampanyasi' if churn_bool else f'Yillik sozlesme teklifinde {float(monthly or 0)*2:.0f}$ indirim sun'}\n"
        f"2. Ucretsiz teknik destek paketini 3 ay hediye et\n"
        f"3. {'Rakip fiyat eslestirme teklifi sun' if churn_bool else 'Sadakat puani programina ekle'}\n"
        f"4. {internet} servisini upgrade et veya fiyat-avantaj karsilastirmasi sun"
    )
    return make_ex(user_msg, response)


def convert_segmentation(row: dict):
    """kaushiksuresh147/customer-segmentation"""
    gender    = safe(row.get("Gender", ""))
    married   = safe(row.get("Ever_Married", row.get("Marital_Status", "")))
    age       = safe(row.get("Age", ""))
    graduated = safe(row.get("Graduated", row.get("Education", "")))
    profession= safe(row.get("Profession", row.get("profession", row.get("Job", ""))))
    spending  = safe(row.get("Spending_Score", row.get("Spending Score (1-100)", "")))
    segment   = safe(row.get("Segmentation", row.get("Category", row.get("Segment", ""))))

    if age == "Bilinmiyor" and profession == "Bilinmiyor":
        return None

    user_msg = (
        f"Bu musteri profilini analiz et:\n\n"
        f"Yas: {age} | Cinsiyet: {gender} | Medeni: {married}\n"
        f"Egitim: {graduated} | Meslek: {profession}\n"
        f"Harcama Skoru: {spending}/100 | Segment: {segment}\n\n"
        f"Bu musteriye hangi urun/hizmet sunulmali? Pazarlama mesaji nasil sekillenmeli?"
    )
    response = (
        f"Musteri Segmentasyon Analizi\n\n"
        f"Segment: {segment}\n"
        f"Profil: {age} yas, {profession}, Harcama: {spending}/100\n\n"
        f"Psikolojik Profil:\n"
        f"- {'Yuksek harcama skoru = premium urunlere acik, kalite odakli karar verir' if float(spending or 0) > 60 else 'Dusuk harcama skoru = fiyat duyarli, deger-odakli mesajlama yap'}\n"
        f"- Meslek {profession}: {'Profesyonel = verimlilik ve zaman tasarrufu on planda' if profession in ['Professional', 'Engineer', 'Doctor', 'Lawyer'] else 'Genel hedef kitle'}\n"
        f"- {graduated} = {'Akademik argumanlara ve veri odakli icerige acik' if str(graduated).lower() == 'yes' else 'Gorsel ve kullanim kolayligina odaklanilan icerik'}\n\n"
        f"Pazarlama Onerileri:\n"
        f"1. Kanal: {'LinkedIn + profesyonel icerik' if profession in ['Professional', 'Engineer', 'Doctor'] else 'Instagram + gorsel odakli icerik'}\n"
        f"2. Mesaj: {'ROI ve verimlilik odakli' if float(spending or 0) > 60 else 'Fiyat avantaji ve deger odakli'}\n"
        f"3. Urun: {segment} segmenti icin ozellestirilmis teklif paketi hazirla\n"
        f"4. Timing: {age} yas grubunun en aktif oldugu {'aksam saatleri' if float(age or 0) < 35 else 'iston saatler'} icin reklam zamanla"
    )
    return make_ex(user_msg, response)


def convert_digital_conversion(row: dict):
    """rabieelkharoua/predict-conversion-in-digital-marketing-dataset"""
    age           = safe(row.get("Age", ""))
    gender        = safe(row.get("Gender", ""))
    income        = safe(row.get("Income", ""))
    campaign_type = safe(row.get("CampaignType", row.get("Campaign_Type", "")))
    ad_spend      = safe(row.get("AdSpend", row.get("Ad_Spend", "")))
    ctr           = safe(row.get("ClickThroughRate", row.get("CTR", "")))
    conv_rate     = safe(row.get("ConversionRate", row.get("Conversion_Rate", "")))
    converted     = safe(row.get("Converted", row.get("converted", "")))
    channel       = safe(row.get("ChannelUsed", row.get("Channel", "")))

    if age == "Bilinmiyor" and campaign_type == "Bilinmiyor":
        return None

    conv_bool = str(converted).lower() in ["1", "yes", "true"]

    user_msg = (
        f"Bu dijital pazarlama kampanyasinin donusum analizini yap:\n\n"
        f"Hedef: {age} yas, {gender}, Gelir: ${income}\n"
        f"Kampanya: {campaign_type} | Kanal: {channel}\n"
        f"Reklam Harcamasi: ${ad_spend} | CTR: {ctr} | CVR: {conv_rate}\n"
        f"Donusum Gerceklesti mi: {converted}\n\n"
        f"Bu kampanyanin etkinligini degerlendirin ve optimize etme yollari neler?"
    )
    response = (
        f"Dijital Pazarlama Donusum Analizi\n\n"
        f"Sonuc: {'DONUSUM GERCEKLESTI' if conv_bool else 'DONUSUM GERCEKLESMEDI'}\n"
        f"Kampanya: {campaign_type} via {channel}\n\n"
        f"Performans Degerlendirmesi:\n"
        f"- CTR {ctr}: {'Ortalama ustunde, ilgi var' if float(ctr or 0) > 0.019 else 'Ortalama altinda, kreatif iyilestir'}\n"
        f"- CVR {conv_rate}: {'Iyi donusum orani' if float(conv_rate or 0) > 0.025 else 'Dusuk — landing page optimize et'}\n"
        f"- Harcama ${ad_spend}: {'CAC (maliyet/donusum) hesapla ve LTV ile karsilastir' if conv_bool else 'Harcama var ama donusum gerceklesmedi — hedefleme gozden gecir'}\n\n"
        f"Hedef Kitle Optimizasyonu:\n"
        f"1. {age} yas, {gender}, ${income} gelir segmenti icin ozel mesajlama yap\n"
        f"2. {'Bu kanal-kampanya kombinasyonu calisıyor — budge artir' if conv_bool else f'{channel} kanali bu hedef kitle icin calismiyor — alternatif kanal dene'}\n"
        f"3. Lookalike audience: Donusum yapan segmentin profilinden LAL olustur\n"
        f"4. Retargeting: {'Donusum yapti — upsell/cross-sell kampanyasi baslat' if conv_bool else 'Donusum yapmadi — 7 gun sonra farkli mesajla tekrar goster'}"
    )
    return make_ex(user_msg, response)


# ─────────────────────────────────────────────────────────────────────────────
# Kaggle Dataset Listesi (tablosal)
# ─────────────────────────────────────────────────────────────────────────────

TABULAR_DATASETS = [
    {
        "id": "madislemsalu/facebook-ad-campaign",
        "desc": "Facebook Ad Campaign Performance",
        "converter": convert_facebook_ad,
    },
    {
        "id": "manishabhatt22/marketing-campaign-performance-dataset",
        "desc": "Marketing Campaign Performance",
        "converter": convert_marketing_perf,
    },
    {
        "id": "zeesolver/consumer-behavior-and-shopping-habits-dataset",
        "desc": "Consumer Behavior & Shopping Habits",
        "converter": convert_consumer_behavior,
    },
    {
        "id": "uom190346a/e-commerce-customer-behavior-dataset",
        "desc": "E-Commerce Customer Behavior",
        "converter": convert_ecommerce_behavior,
    },
    {
        "id": "faviovaz/marketing-ab-testing",
        "desc": "Marketing A/B Testing",
        "converter": convert_ab_test_full,
    },
    {
        "id": "blastchar/telco-customer-churn",
        "desc": "Telco Customer Churn",
        "converter": convert_churn_full,
    },
    {
        "id": "kaushiksuresh147/customer-segmentation",
        "desc": "Customer Segmentation Classification",
        "converter": convert_segmentation,
    },
    {
        "id": "rabieelkharoua/predict-conversion-in-digital-marketing-dataset",
        "desc": "Predict Conversion in Digital Marketing",
        "converter": convert_digital_conversion,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# İndirme + Dönüştürme
# ─────────────────────────────────────────────────────────────────────────────

def download_dataset(dataset_id: str, dest: str) -> bool:
    try:
        import kaggle
        print(f"  Indiriliyor: {dataset_id}...")
        kaggle.api.dataset_download_files(dataset_id, path=dest, unzip=True, quiet=False)
        return True
    except Exception as e:
        print(f"  HATA ({dataset_id}): {e}")
        return False


def process_directory(data_dir: str, converter, out_f) -> int:
    count = 0
    files = (glob.glob(os.path.join(data_dir, "**/*.csv"), recursive=True) +
             glob.glob(os.path.join(data_dir, "**/*.json"), recursive=True))

    for fpath in files:
        try:
            if fpath.endswith(".csv"):
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    for row in tqdm(csv.DictReader(f), desc=f"  {os.path.basename(fpath)}", leave=False):
                        ex = converter(row)
                        if ex:
                            out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                            count += 1
            elif fpath.endswith(".json"):
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for row in tqdm(data, desc=f"  {os.path.basename(fpath)}", leave=False):
                            ex = converter(row)
                            if ex:
                                out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                                count += 1
        except Exception as e:
            print(f"  Dosya hatasi ({fpath}): {e}")
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",   default=OUTPUT_FILE)
    parser.add_argument("--data-dir", default=KAGGLE_DATA_DIR)
    parser.add_argument("--skip-download", action="store_true",
                        help="Indirmeyi atla, sadece var olan dosyaları donustur")
    args = parser.parse_args()

    import csv  # noqa — used in process_directory
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    total = 0
    print(f"\nTablosal Dataset Donusum Baslaniyor")
    print(f"Cikti: {args.output}\n")

    with open(args.output, 'w', encoding='utf-8') as out_f:
        for ds in TABULAR_DATASETS:
            ds_id     = ds["id"]
            ds_name   = ds_id.split("/")[1]
            converter = ds["converter"]
            dest      = os.path.join(args.data_dir, ds_name)

            print(f"\n{'='*50}")
            print(f"Dataset: {ds_id}")
            print(f"Aciklama: {ds['desc']}")

            if not args.skip_download:
                ok = download_dataset(ds_id, dest)
                if not ok:
                    print("  ATLANIYOR.")
                    continue
            elif not os.path.exists(dest):
                print(f"  {dest} bulunamadi, atlaniyor.")
                continue

            count = process_directory(dest, converter, out_f)
            print(f"  {count:,} ornek uretildi.")
            total += count

    print(f"\n{'='*50}")
    print(f"TAMAMLANDI — Toplam: {total:,} tablosal ornek")
    print(f"Cikti: {args.output}")


if __name__ == "__main__":
    main()
