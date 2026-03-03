import os
import urllib.request
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

D_DRIVE_PATH = "D:/datasets/sales_marketing/other_sources"
os.makedirs(D_DRIVE_PATH, exist_ok=True)

OTHER_URLS = [
    # GitHub / Repolar (Genellikle zip olarak indireceğiz)
    {"name": "PolyAI-conversational", "url": "https://github.com/PolyAI-LDN/conversational-datasets/archive/refs/heads/master.zip"},
    {"name": "Facebook-Negotiator", "url": "https://github.com/facebookresearch/end-to-end-negotiator/archive/refs/heads/master.zip"},
    {"name": "DebateSum", "url": "https://github.com/Hellisotherpeople/DebateSum/archive/refs/heads/master.zip"},
    {"name": "BadAdsData", "url": "https://github.com/eric-zeng/conpro-bad-ads-data/archive/refs/heads/master.zip"},
    {"name": "AdsRecSys", "url": "https://github.com/Atomu2014/Ads-RecSys-Datasets/archive/refs/heads/master.zip"},
    {"name": "Clickbait", "url": "https://github.com/bhargaviparanjape/clickbait/archive/refs/heads/master.zip"},
    
    # Standart / Arxiv Kaynakları (Erişilebilir data linkleri bulunana yönelenler)
    {"name": "Online-Shoppers-UCI", "url": "https://archive.ics.uci.edu/static/public/468/online+shoppers+purchasing+intention+dataset.zip"},
    {"name": "Online-Retail-UCI", "url": "https://archive.ics.uci.edu/static/public/352/online+retail.zip"},
    {"name": "Iranian-Churn-UCI", "url": "https://archive.ics.uci.edu/static/public/563/iranian+churn+dataset.zip"},
]

def download_others():
    for item in OTHER_URLS:
        name = item["name"]
        url = item["url"]
        
        target_path = os.path.join(D_DRIVE_PATH, f"{name}.zip")
        
        if os.path.exists(target_path):
            logger.info(f"[Atlanıyor] Zaten yüklü: {name}")
            continue
            
        logger.info(f"[İndiriliyor] {name} -> {target_path}")
        try:
            # Standart urllib downloader
            urllib.request.urlretrieve(url, target_path)
            logger.info(f"Başarı: {name}")
        except Exception as e:
            logger.error(f"Hata ({name}): {e}")

def process_other_to_jsonl():
    logger.info("Diğer verileri JSONL'e ekleme başlatılıyor...")
    output_file = "D:/datasets/sales_marketing/external_training_data.jsonl"
    
    # Burada indirilen ziplerin açılıp işlenme mantığı yer alır.
    # Şimdilik framework olarak yerini ayırıyoruz.
    logger.info(f"Diğer veriler de {output_file} içine eklenecek şeklinde yapılandırıldı.")

if __name__ == "__main__":
    logger.info("Diğer (Other) Kaynakları İndirme Pipeline'ı Başlatılıyor...")
    download_others()
    process_other_to_jsonl()
