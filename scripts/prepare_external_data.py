"""
Kaggle & External Dataset Parser — Tam Kapsamlı
=================================================
D:/datasets/sales_marketing/ altındaki TÜM CSV/JSON/TSV dosyalarını tarar,
her birinin kolon yapısını analiz eder ve LLM instruction formatına (JSONL)
dönüştürüp external_training_data.jsonl dosyasına yazar.
"""

import os
import json
import glob
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(message)s')
logger = logging.getLogger(__name__)

D_DRIVE_PATH = "D:/datasets/sales_marketing"
OUTPUT_FILE = os.path.join(D_DRIVE_PATH, "external_training_data.jsonl")

# ============================================================
# AKILLI KOLON TANIMA VE PROMPT OLUŞTURMA
# ============================================================

# Kategori bazlı prompt şablonları
CATEGORY_PROMPTS = {
    "sales": "Bu satış verisini analiz et ve satış stratejisi önerilerinde bulun.",
    "crm": "Bu CRM verisini analiz et. Müşteri ilişkileri ve satış fırsatları hakkında değerlendirme yap.",
    "ads": "Bu reklam kampanya verisini analiz et. Performans metrikleri ve optimizasyon önerileri sun.",
    "facebook": "Bu Facebook/Meta reklam verisini analiz et. Hedef kitle ve bütçe optimizasyonu öner.",
    "google": "Bu Google Ads verisini analiz et. Anahtar kelime ve bidding stratejisi öner.",
    "email": "Bu email pazarlama verisini analiz et. Açılma/tıklama oranları ve A/B test önerileri sun.",
    "ecommerce": "Bu e-ticaret verisini analiz et. Müşteri davranışı ve satış artırma stratejileri öner.",
    "consumer": "Bu tüketici davranış verisini analiz et. Segmentasyon ve hedefleme önerileri sun.",
    "churn": "Bu müşteri kayıp verisini analiz et. Churn önleme stratejileri ve retention taktikleri öner.",
    "ctr": "Bu tıklama oranı verisini analiz et. CTR optimizasyonu ve reklam yerleşimi önerileri sun.",
    "review": "Bu müşteri yorumunu analiz et. Duygu analizi yap ve ürün iyileştirme önerileri sun.",
    "headline": "Bu başlığı analiz et. Dikkat çekici ve tıklama oranı yüksek başlık yazma teknikleri öner.",
    "ab_test": "Bu A/B test verisini analiz et. İstatistiksel anlamlılık ve kazanan varyantı değerlendir.",
    "segmentation": "Bu müşteri segmentasyon verisini analiz et. Hedef kitle profilleri oluştur.",
    "marketing": "Bu dijital pazarlama verisini analiz et. Kampanya performansı ve ROI değerlendirmesi yap.",
    "ner": "Bu metin verisindeki önemli varlıkları (isim, şirket, yer, ürün) tanımla ve etiketle.",
    "generic": "Bu veriyi analiz et ve satış/pazarlama perspektifinden değerlendirme yap."
}

def detect_category(folder_name: str) -> str:
    """Klasör adından veri kategorisini tespit et."""
    name = folder_name.lower()
    if "sales" in name or "crm" in name or "pipeline" in name:
        return "crm"
    elif "facebook" in name or "meta" in name:
        return "facebook"
    elif "google" in name:
        return "google"
    elif "email" in name:
        return "email"
    elif "ecommerce" in name or "e-commerce" in name or "shopping" in name or "instacart" in name:
        return "ecommerce"
    elif "consumer" in name or "customer" in name or "purchasing" in name:
        return "consumer"
    elif "churn" in name:
        return "churn"
    elif "click" in name or "ctr" in name or "ad" in name:
        return "ctr"
    elif "review" in name or "clothing" in name or "amazon" in name:
        return "review"
    elif "headline" in name or "sarcasm" in name or "clickbait" in name or "slogan" in name or "post-generator" in name:
        return "headline"
    elif "ab-test" in name or "ab_test" in name:
        return "ab_test"
    elif "segment" in name:
        return "segmentation"
    elif "marketing" in name or "campaign" in name or "digital" in name or "political" in name:
        return "marketing"
    elif "ner" in name or "entity" in name:
        return "ner"
    else:
        return "generic"


def row_to_instruction(row: dict, category: str, columns: list) -> dict | None:
    """Tek bir satırı instruction/input/output formatına çevir."""
    prompt = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS["generic"])

    # Satırdaki tüm değerleri toplayıp anlamlı bir input oluştur
    parts = []
    for col in columns:
        val = row.get(col, "")
        if val is not None and str(val).strip() and str(val).lower() != "nan":
            parts.append(f"{col}: {str(val)[:500]}")

    if not parts or len(parts) < 2:
        return None

    input_txt = "\n".join(parts[:15])  # En fazla 15 kolon

    # Akıllı output oluşturma (veri tipine göre)
    output_parts = []
    for col in columns:
        val = row.get(col, "")
        if val is None or str(val).lower() == "nan" or not str(val).strip():
            continue
        val_str = str(val)[:300]

        # Spesifik kolon isimlerinden anlam çıkar
        col_lower = col.lower()
        if any(k in col_lower for k in ["label", "sentiment", "class", "target", "churn", "result", "outcome"]):
            output_parts.append(f"Sonuç/Etiket: {val_str}")
        elif any(k in col_lower for k in ["price", "revenue", "cost", "spend", "budget", "amount", "salary"]):
            output_parts.append(f"Finansal Değer ({col}): {val_str}")
        elif any(k in col_lower for k in ["click", "ctr", "impression", "conversion", "rate", "score"]):
            output_parts.append(f"Performans Metriği ({col}): {val_str}")
        elif any(k in col_lower for k in ["text", "review", "comment", "body", "content", "description", "headline", "title", "subject", "ad_text", "slogan"]):
            output_parts.append(f"Metin İçeriği: {val_str}")

    if not output_parts:
        # Genel fallback: İlk 3 kolonu özetle
        for col in columns[:3]:
            val = row.get(col, "")
            if val is not None and str(val).strip() and str(val).lower() != "nan":
                output_parts.append(f"{col}: {str(val)[:200]}")

    if not output_parts:
        return None

    output_txt = (
        f"Bu {category} verisinin analizi:\n"
        + "\n".join(output_parts[:8])
        + f"\n\nÖneri: Bu verilere dayanarak {CATEGORY_PROMPTS.get(category, 'strateji geliştir')}."
    )

    return {
        "instruction": prompt,
        "input": input_txt[:3000],
        "output": output_txt[:3000]
    }


def parse_csv_file(filepath: str, category: str, max_rows: int = None) -> list[dict]:
    """Bir CSV dosyasını parse edip instruction listesi döndür."""
    results = []
    try:
        for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                df = pd.read_csv(filepath, nrows=max_rows, encoding=enc, on_bad_lines='skip')
                break
            except (UnicodeDecodeError, Exception):
                continue
        else:
            logger.warning(f"  [ATLA] Encoding okunamadı: {filepath}")
            return []

        columns = list(df.columns)
        logger.info(f"  Kolonlar: {columns[:10]}{'...' if len(columns) > 10 else ''} ({len(df)} satır)")

        for _, row in df.iterrows():
            record = row_to_instruction(row.to_dict(), category, columns)
            if record:
                results.append(record)

    except Exception as e:
        logger.error(f"  CSV parse hatası: {e}")
    
    return results


def parse_json_file(filepath: str, category: str, max_rows: int = 50000) -> list[dict]:
    """Bir JSON dosyasını parse edip instruction listesi döndür."""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # JSON Lines formatı mı?
        if content.startswith('{') and '\n' in content:
            lines = content.split('\n')
            for line in lines[:max_rows]:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        columns = list(item.keys())
                        record = row_to_instruction(item, category, columns)
                        if record:
                            results.append(record)
                except json.JSONDecodeError:
                    continue
        else:
            # Normal JSON array
            data = json.loads(content)
            if isinstance(data, list):
                for item in data[:max_rows]:
                    if isinstance(item, dict):
                        columns = list(item.keys())
                        record = row_to_instruction(item, category, columns)
                        if record:
                            results.append(record)
            elif isinstance(data, dict):
                # Tek obje — direkt parse et
                columns = list(data.keys())
                record = row_to_instruction(data, category, columns)
                if record:
                    results.append(record)

    except Exception as e:
        logger.error(f"  JSON parse hatası: {e}")
    
    return results


def parse_tsv_file(filepath: str, category: str, max_rows: int = 50000) -> list[dict]:
    """Bir TSV dosyasını parse edip instruction listesi döndür."""
    results = []
    try:
        df = pd.read_csv(filepath, sep='\t', nrows=max_rows, on_bad_lines='skip')
        columns = list(df.columns)
        for _, row in df.iterrows():
            record = row_to_instruction(row.to_dict(), category, columns)
            if record:
                results.append(record)
    except Exception as e:
        logger.error(f"  TSV parse hatası: {e}")
    return results


# ============================================================
# ANA PIPELINE
# ============================================================

def process_all_to_jsonl():
    """D diskindeki TÜM veri klasörlerini tarar ve JSONL'e yazar."""
    logger.info("=" * 60)
    logger.info("🚀 TAM KAPSAMLI D DİSKİ VERİ PARSE İŞLEMİ BAŞLIYOR")
    logger.info(f"   Kaynak: {D_DRIVE_PATH}")
    logger.info(f"   Hedef:  {OUTPUT_FILE}")
    logger.info("=" * 60)

    total_records = 0
    total_files = 0
    skipped_folders = []

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        # D diskindeki her klasörü tara
        for folder_name in sorted(os.listdir(D_DRIVE_PATH)):
            folder_path = os.path.join(D_DRIVE_PATH, folder_name)
            
            # Sadece klasörleri işle (jsonl çıktı dosyasını atla)
            if not os.path.isdir(folder_path):
                continue
            if folder_name == "other_sources":
                continue  # Other sources ayrı işlenecek

            category = detect_category(folder_name)
            
            # Bu klasördeki tüm veri dosyalarını bul
            data_files = []
            for ext in ['*.csv', '*.json', '*.jsonl', '*.tsv', '*.txt']:
                data_files.extend(glob.glob(os.path.join(folder_path, '**', ext), recursive=True))
            
            if not data_files:
                skipped_folders.append(folder_name)
                continue

            logger.info(f"\n📂 {folder_name} ({category}) — {len(data_files)} dosya")

            folder_records = 0
            for fpath in data_files:
                fname = os.path.basename(fpath)
                fext = fname.rsplit('.', 1)[-1].lower()
                fsize_mb = os.path.getsize(fpath) / (1024 * 1024)

                logger.info(f"  📄 {fname} ({fsize_mb:.1f} MB, sınırsız)")

                records = []
                if fext == 'csv':
                    records = parse_csv_file(fpath, category)
                elif fext in ('json', 'jsonl'):
                    records = parse_json_file(fpath, category)
                elif fext == 'tsv':
                    records = parse_tsv_file(fpath, category)
                elif fext == 'txt':
                    # TXT dosyalarını CSV gibi okumayı dene
                    records = parse_csv_file(fpath, category)

                # JSONL'e yaz
                for record in records:
                    try:
                        json_line = json.dumps(record, ensure_ascii=False)
                        # Surrogate karakterleri temizle
                        json_line = json_line.encode('utf-8', errors='replace').decode('utf-8')
                        out_f.write(json_line + "\n")
                        folder_records += 1
                        total_records += 1
                    except Exception:
                        continue  # Bozuk karakter varsa atla

                total_files += 1
                logger.info(f"     ✅ {len(records):,} kayıt parse edildi")

            logger.info(f"  📊 Klasör Toplamı: {folder_records:,} kayıt")

    logger.info("\n" + "=" * 60)
    logger.info(f"🏆 PARSE TAMAMLANDI!")
    logger.info(f"   Toplam Dosya: {total_files}")
    logger.info(f"   Toplam Kayıt: {total_records:,}")
    logger.info(f"   Çıktı: {OUTPUT_FILE}")
    if skipped_folders:
        logger.info(f"   Atlanan Boş Klasörler: {skipped_folders}")
    logger.info("=" * 60)


if __name__ == "__main__":
    process_all_to_jsonl()
