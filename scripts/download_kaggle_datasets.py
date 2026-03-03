"""
download_kaggle_datasets.py
============================
H200 sunucusunda calistir.
Metin tabanli Kaggle datasetlerini indirir, Qwen3-VL Thinking formatina
donusturur ve /workspace/models/tmp/kaggle_data.jsonl dosyasina yazar.

Kullanim:
    python scripts/download_kaggle_datasets.py
    python scripts/download_kaggle_datasets.py --output /workspace/models/tmp/kaggle_data.jsonl
"""

import os
import sys
import json
import zipfile
import argparse
import glob
from pathlib import Path
from tqdm import tqdm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KAGGLE_DATA_DIR = "/workspace/data/kaggle"
OUTPUT_FILE     = "/workspace/models/tmp/kaggle_data.jsonl"

SYSTEM_PROMPT = """Sen bir satis psikolojisi ve dijital reklam stratejisi uzmanisın.
Turkiye ve global pazarlari iyi bilirsin."""

def think_wrap(instruction: str, response: str) -> str:
    preview = instruction[:120].replace("\n", " ")
    return (
        f"<think>\n"
        f"Bu soruyu analiz ediyorum: {preview}\n"
        f"En dogru ve yararli yaniti olusturuyorum.\n"
        f"</think>\n\n"
        f"{response}"
    )

def make_example(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": user[:3000]},
            {"role": "assistant", "content": think_wrap(user, assistant[:3000])},
        ]
    }

# ─────────────────────────────────────────────────────────────────────────────
# Dataset tanımları
# ─────────────────────────────────────────────────────────────────────────────

KAGGLE_DATASETS = [
    # [id, kaggle_path, description, converter_func_name]
    {
        "id": "amananandrai/clickbait-dataset",
        "desc": "Clickbait vs Non-Clickbait Headlines",
        "converter": "convert_clickbait",
    },
    {
        "id": "chaibapat/slogan-dataset",
        "desc": "Brand Slogans & Taglines",
        "converter": "convert_slogan",
    },
    {
        "id": "nicapotato/womens-ecommerce-clothing-reviews",
        "desc": "Womens E-Commerce Clothing Reviews",
        "converter": "convert_review",
    },
    {
        "id": "rmisra/news-headlines-dataset-for-sarcasm-detection",
        "desc": "Sarcasm Detection in Headlines",
        "converter": "convert_sarcasm",
    },
    {
        "id": "rahulchavan99/marketing-campaign-dataset",
        "desc": "Marketing Campaign Performance",
        "converter": "convert_marketing_campaign",
    },
    {
        "id": "prishatank/post-generator-dataset",
        "desc": "Social Media Post Generator",
        "converter": "convert_social_post",
    },
    {
        "id": "faviovaz/marketing-ab-testing",
        "desc": "Marketing A/B Testing Dataset",
        "converter": "convert_ab_test",
    },
    {
        "id": "bittlingmayer/amazonreviews",
        "desc": "Amazon Reviews Sentiment",
        "converter": "convert_amazon_review",
    },
    {
        "id": "blastchar/telco-customer-churn",
        "desc": "Telco Customer Churn",
        "converter": "convert_churn",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Converter fonksiyonları
# ─────────────────────────────────────────────────────────────────────────────

def convert_clickbait(row: dict) -> dict | None:
    headline = row.get("headline", row.get("title", row.get("text", "")))
    label    = row.get("clickbait", row.get("label", ""))
    if not headline:
        return None
    label_str = "Clickbait" if str(label) in ["1","true","True","clickbait"] else "Normal haber basligi"
    return make_example(
        f"Bu haber basligi clickbait mi? Reklam ve pazarlama acisindan degerlendir:\n\n{headline}",
        f"Baslik turu: {label_str}\n\nBu baslik {'dikkat cekme amacli yazilmis, merak uyandiriyor ve kullanicinin tiklamasini saglamak icin belirsizlik kullaniyor.' if label_str == 'Clickbait' else 'olgusal ve dogrudan, clickbait degil.'}\n\nPazarlama aciklaması: {'Benzer yontemleri reklam basliklarinda kullanmak CTR artisina yardimci olabilir, ancak dikkat: kotu clickbait marka guvenilirligini dusurebilir.' if label_str == 'Clickbait' else 'Guvenilir marka iletisimi icin bu tur seffaf basliklar tercih edilmeli.'}"
    )


def convert_slogan(row: dict) -> dict | None:
    slogan = row.get("slogan", row.get("text", row.get("tagline", "")))
    brand  = row.get("brand", row.get("company", row.get("name", "")))
    if not slogan or len(str(slogan)) < 5:
        return None
    user_msg = f"Bu slogan/tagline'i reklam psikolojisi perspektifinden analiz et:\n\n"
    if brand:
        user_msg += f"Marka: {brand}\n"
    user_msg += f"Slogan: {slogan}"
    return make_example(
        user_msg,
        f"Bu slogan '{slogan}' sunlari basariyor:\n\n1. Kisa ve akilda kalici\n2. Marka vaadini net ifade ediyor\n3. Duygusal bag kuruyor\n\nBenzer bir slogan uluslararasi pazara hitap edecek sekilde duzenlenebilir."
    )


def convert_review(row: dict) -> dict | None:
    review_text = row.get("Review Text", row.get("review_text", row.get("text", "")))
    rating      = row.get("Rating", row.get("rating", ""))
    title       = row.get("Title", row.get("title", ""))
    if not review_text or len(str(review_text)) < 30:
        return None
    return make_example(
        f"Bu musteri yorumunu satis ve pazarlama acısından analiz et:\n\nYorum basligı: {title}\nPuan: {rating}/5\n\n{str(review_text)[:2000]}",
        f"Musteri Yorum Analizi:\n\nPuan {rating}/5 olan bu yorumda musteri {'memnuniyetini' if str(rating) in ['4','5'] else 'memnuniyetsizligini'} dile getiriyor.\n\nPazarlama cikarimlari:\n- Bu tur geri bildirimler urun sayfasinda sosyal kanit olarak kullanilabilir\n- {'Olumlu yorum: Reklam materyalinde quote olarak yer alabilir' if str(rating) in ['4','5'] else 'Olumsuz yorum: Urun gelistirmede once ele alinmali'}"
    )


def convert_sarcasm(row: dict) -> dict | None:
    headline  = row.get("headline", row.get("text", ""))
    is_sarcasm = row.get("is_sarcastic", row.get("label", 0))
    if not headline:
        return None
    return make_example(
        f"Bu haber basligi sarkastik mi? Reklam basligi yazarken bu tarzdan ne ogrenebiliriz?\n\n{headline}",
        f"Bu baslik {'sarkastik/ironic bir ton tasiyor' if str(is_sarcasm) in ['1','True','true'] else 'dogrudan ve literal'}.\n\nReklam basligi yaziminda ironi kullanimi:\n- Dogru hedef kitleyle kullanildiginda dikkat ceker\n- Risk: hedef kitle tarafindan yanlis anlasilabilir\n- Tavsiye: A/B test ile test edip dogrudan vs ironik basligi karsilastir"
    )


def convert_marketing_campaign(row: dict) -> dict | None:
    channel  = row.get("Channel_Used", row.get("channel", ""))
    campaign = row.get("Campaign_Type", row.get("campaign_type", ""))
    conv_rate = row.get("Conversion_Rate", row.get("conversion_rate", ""))
    roi      = row.get("ROI", row.get("roi", ""))
    if not channel and not campaign:
        return None
    return make_example(
        f"Bu pazarlama kampanyasini analiz et ve optimizasyon onerisi sun:\n\nKanal: {channel}\nKampanya turu: {campaign}\nDonusum orani: {conv_rate}\nROI: {roi}",
        f"Kampanya Analizi:\n\nKanal '{channel}' uzerinden yurutulen bu {campaign} kampanyasinda donusum orani {conv_rate} ve ROI {roi} olarak gozuklmektedir.\n\nOptimizasyon onerileri:\n1. Hedef kitle segmentasyonunu gozden gecir\n2. Urun-kanal uyumunu test et\n3. Mesaj ozellesitirmesini artir"
    )


def convert_social_post(row: dict) -> dict | None:
    topic    = row.get("Topic", row.get("topic", row.get("category", "")))
    platform = row.get("Platform", row.get("platform", "Social Media"))
    post     = row.get("Post", row.get("post", row.get("text", row.get("content", ""))))
    if not post or len(str(post)) < 20:
        return None
    return make_example(
        f"{platform} icin {topic} konusunda etkileyici bir sosyal medya gonderisi yaz veya bu gonderiyi analiz et:\n\n{str(post)[:1500]}",
        f"Bu {platform} gonderisi su teknikleri kullaniyor:\n\n1. Dikkat cekici acilis\n2. Icerik degerini hizlica iletme\n3. Engage edici dil\n\nMarketingde bu tur icerik: %3-5 uzerinde engagement rate hedeflemeli."
    )


def convert_ab_test(row: dict) -> dict | None:
    group     = row.get("test group", row.get("group", ""))
    converted = row.get("converted", row.get("conversion", ""))
    ads_seen  = row.get("total ads", row.get("ads", ""))
    if not group:
        return None
    return make_example(
        f"Bu A/B test sonucunu yorumla:\n\nTest grubu: {group}\nDonusum: {converted}\nGorulen reklam sayisi: {ads_seen}",
        f"A/B Test Analizi:\n\nGrup '{group}': {'Reklam goren kullanicilarin' if group == 'ad' else 'Kontrol grubunun (PSA)'} donusum orani inceleniyor.\n\nSonuc yorumu:\n- {group} grubunun performansini kontrol grubuyla karsilastir\n- Istatistiksel anlamlilik icin p<0.05 olmasi gerekir\n- Pratik anlam icin donusum farki >%1 olmali"
    )


def convert_amazon_review(row: dict) -> dict | None:
    text  = row.get("text", row.get("review", ""))
    label = row.get("label", row.get("sentiment", ""))
    if not text:
        return None
    sentiment = "Pozitif" if str(label) in ["2","1","positive","Positive"] else "Negatif"
    return make_example(
        f"Bu Amazon urun yorumunun duygusunu belirle ve pazarlama perspektifinden degerlendir:\n\n{str(text)[:2000]}",
        f"Duygu Analizi: {sentiment}\n\nBu {'olumlu' if sentiment == 'Pozitif' else 'olumsuz'} yorum pazarlama icin sunlari ifade ediyor:\n- {'Urun sayfasinda testimonial olarak kullanilabilir' if sentiment == 'Pozitif' else 'Acil urun/hizmet iyilestirmesi gerektiriyor'}\n- Musteri sesi (VoC) analizi icin veri noktasi\n- Rakip analizi ve benchmark icin referans"
    )


def convert_churn(row: dict) -> dict | None:
    tenure   = row.get("tenure", "")
    monthly  = row.get("MonthlyCharges", "")
    churn    = row.get("Churn", "")
    contract = row.get("Contract", "")
    if not churn:
        return None
    return make_example(
        f"Bu musteri profilini analiz et. Churn riski ve satis stratejisi onerisi sun:\n\nSozlesme: {contract}\nAylik ucret: {monthly}\nSuresi: {tenure} ay\nChurn: {churn}",
        f"Musteri Churn Analizi:\n\nBu musteri {'churn etmis' if str(churn) == 'Yes' else 'aktif musteri'}.\n\nSatis stratejisi:\n{'- Geri kazanma kampanyasi: Indirim veya ucretsiz ay teklifi' if str(churn) == 'Yes' else '- Upsell firsati: Daha yuksek paketlere yonlendir'}\n- Sadakat programina dahil et\n- {'Net Promoter Score dusuk olabilir, hizli mudahale gerekiyor' if str(churn) == 'Yes' else 'Referral programi icin uygun profil'}"
    )


CONVERTER_MAP = {
    "convert_clickbait":         convert_clickbait,
    "convert_slogan":            convert_slogan,
    "convert_review":            convert_review,
    "convert_sarcasm":           convert_sarcasm,
    "convert_marketing_campaign": convert_marketing_campaign,
    "convert_social_post":       convert_social_post,
    "convert_ab_test":           convert_ab_test,
    "convert_amazon_review":     convert_amazon_review,
    "convert_churn":             convert_churn,
}


# ─────────────────────────────────────────────────────────────────────────────
# Download + Convert
# ─────────────────────────────────────────────────────────────────────────────

def download_dataset(dataset_id: str, dest_dir: str) -> str | None:
    try:
        import kaggle
        print(f"  Indiriliyor: {dataset_id}")
        kaggle.api.dataset_download_files(dataset_id, path=dest_dir, unzip=True, quiet=False)
        return dest_dir
    except Exception as e:
        print(f"  HATA ({dataset_id}): {e}")
        return None


def convert_directory(data_dir: str, converter_name: str, out_f) -> int:
    converter = CONVERTER_MAP.get(converter_name)
    if not converter:
        print(f"  Bilinmeyen converter: {converter_name}")
        return 0

    count = 0
    csv_files = glob.glob(os.path.join(data_dir, "**/*.csv"), recursive=True) + \
                glob.glob(os.path.join(data_dir, "**/*.json"), recursive=True) + \
                glob.glob(os.path.join(data_dir, "**/*.jsonl"), recursive=True)

    for fpath in csv_files:
        try:
            if fpath.endswith(".csv"):
                import csv
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    reader = csv.DictReader(f)
                    for row in tqdm(reader, desc=f"  {os.path.basename(fpath)}", leave=False):
                        example = converter(row)
                        if example:
                            out_f.write(json.dumps(example, ensure_ascii=False) + "\n")
                            count += 1
            elif fpath.endswith((".json", ".jsonl")):
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        try:
                            row = json.loads(line)
                            if isinstance(row, dict):
                                example = converter(row)
                                if example:
                                    out_f.write(json.dumps(example, ensure_ascii=False) + "\n")
                                    count += 1
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"  Dosya okuma hatasi ({fpath}): {e}")
            continue

    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--data-dir", default=KAGGLE_DATA_DIR)
    args = parser.parse_args()

    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    total = 0
    print(f"\nKaggle dataset indirme + donusturme baslaniyor")
    print(f"Cikti: {args.output}\n")

    with open(args.output, 'w', encoding='utf-8') as out_f:
        for ds in KAGGLE_DATASETS:
            ds_id       = ds["id"]
            ds_name     = ds_id.split("/")[1]
            converter   = ds["converter"]
            dest        = os.path.join(args.data_dir, ds_name)

            print(f"\n{'='*50}")
            print(f"Dataset: {ds_id}")
            print(f"Acıklama: {ds['desc']}")

            # 1. Indir
            result = download_dataset(ds_id, dest)
            if result is None:
                print(f"  ATLANIYOR (indirme hatasi)")
                continue

            # 2. Donustur
            count = convert_directory(dest, converter, out_f)
            print(f"  {count:,} ornek eklendi.")
            total += count

    print(f"\n{'='*50}")
    print(f"TAMAMLANDI")
    print(f"Toplam Kaggle ornegi: {total:,}")
    print(f"Cikti dosyasi: {args.output}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
