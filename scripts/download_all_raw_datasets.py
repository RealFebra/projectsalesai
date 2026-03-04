"""
download_all_raw_datasets.py
===========================
Indirilecek veri kaynaklari listesini (compass artifact'ten) tutar ve 
Kaggle, HF vs. fark etmeksizin tum 100+ datayi /workspace/data/raw klasorune ceker.
Bu script sadece VERI INDIRME (raw ingestion) isini yapar.
"""

import os
import argparse
from huggingface_hub import snapshot_download

# Compass artifact icindeki tum gecerli HuggingFace datasetleri
HF_DATASETS = [
    "goendalf666/sales-conversations",
    "goendalf666/sales-conversations-instruction-customer",
    "goendalf666/sales-textbook_for_convincing_and_selling",
    "DeepMostInnovations/saas-sales-conversations",
    "gwenshap/sales-transcripts",
    "AIxBlock/92k-real-world-call-center-scripts-english",
    "AxonData/english-contact-center-audio-dataset",
    "bitext/Bitext-customer-support-llm-chatbot-training-dataset",
    "stanfordnlp/craigslist_bargains",
    "kchawla123/casino",
    "mikelewis0/deal_or_no_dialog",
    "spawn99/PersuasionForGood",
    "Anthropic/persuasion",
    "SemEvalWorkshop/sem_eval_2020_task_11",
    "Yale-LILY/aeslc",
    "smangrul/ad-copy-generation",
    "PeterBrendan/Ads_Creative_Ad_Copy_Programmatic",
    "PeterBrendan/Ads_Creative_Text_Programmatic",
    "PeterBrendan/AdImageNet",
    "cyberagent/AdTEC",
    "c-s-ale/Product-Descriptions-and-Ads",
    "RafaM97/marketing_social_media",
    "criteo/CriteoClickLogs",
    "criteo/CriteoPrivateAd",
    "Ateeqq/Amazon-Product-Description",
    "philschmid/amazon-product-descriptions-vlm",
    "suolyer/copywriting",
    "McAuley-Lab/Amazon-Reviews-2023",
    "fancyzhx/amazon_polarity",
    "Yelp/yelp_review_full",
    "fancyzhx/yelp_polarity",
    "stanfordnlp/sst2",
    "mteb/imdb",
    "mltrev23/financial-sentiment-analysis",
    "Sp1786/multiclass-sentiment-analysis-dataset",
    "stanfordnlp/sentiment140",
    "cardiffnlp/tweet_eval",
    "carblacac/twitter-sentiment-analysis",
    "ZurichNLP/x_stance",
    "yuncongli/chat-sentiment-analysis"
]

# Compass artifact icindeki tum gecerli Kaggle datasetleri
KAGGLE_DATASETS = [
    "ashishpandey5210/sales-pipeline-dataset",
    "innocentmfa/crm-sales-opportunities",
    "wcukierski/enron-email-dataset",
    "madislemsalu/facebook-ad-campaign",
    "aparnashankar/facebook-ads-dataset",
    "mrmorj/political-advertisements-from-facebook",
    "dankawaguchi/google-ads",
    "nayakganesh007/google-ads-sales-dataset",
    "brendan45774/how-much-it-cost-to-get-an-ad-on-google",
    "manishabhatt22/marketing-campaign-performance-dataset",
    "rahulchavan99/marketing-campaign-dataset",
    "rabieelkharoua/predict-conversion-in-digital-marketing-dataset",
    "allyjung81/digital-marketing-dataset",
    "ziya07/social-media-ad-dataset",
    "ashydv/advertising-dataset",
    "loveall/email-campaign-management-for-sme",
    "mariusnikiforovas/email-marketing-campaign-dashboard",
    "faviovaz/marketing-ab-testing",
    "amirmotefaker/ab-testing-dataset",
    "c/criteo-display-ad-challenge",
    "gabrielsantello/advertisement-click-on-ad",
    "swekerr/click-through-rate-prediction",
    "c/avazu-ctr-prediction",
    "c/talkingdata-adtracking-fraud-detection",
    "amananandrai/clickbait-dataset",
    "rmisra/news-headlines-dataset-for-sarcasm-detection",
    "anil1055/english-headlines-dataset",
    "chaibapat/slogan-dataset",
    "piyushjain16/amazon-product-data",
    "prishatank/post-generator-dataset",
    "zeesolver/consumer-behavior-and-shopping-habits-dataset",
    "uom190346a/e-commerce-customer-behavior-dataset",
    "rabieelkharoua/predict-customer-purchase-behavior-dataset",
    "hanaksoy/customer-purchasing-behaviors",
    "ziya07/ai-driven-consumer-behavior-dataset",
    "thedevastator/online-shopping-consumer-behavior-dataset",
    "mkechinov/ecommerce-behavior-data-from-multi-category-store",
    "psparks/instacart-market-basket-analysis",
    "tunguz/clickstream-data-for-online-shopping",
    "retailrocket/ecommerce-dataset",
    "blastchar/telco-customer-churn",
    "vjchoudhary7/customer-segmentation-tutorial-in-python",
    "kaushiksuresh147/customer-segmentation",
    "bittlingmayer/amazonreviews",
    "nicapotato/womens-ecommerce-clothing-reviews",
    "debasisdotcom/name-entity-recognition-ner-dataset"
]


def download_hf(base_dir):
    print(f"\n[{len(HF_DATASETS)}] HuggingFace dataseti indiriliyor...")
    hf_dir = os.path.join(base_dir, "hf")
    os.makedirs(hf_dir, exist_ok=True)
    
    for ds in HF_DATASETS:
        print(f"  Downloading -> {ds}")
        try:
            snapshot_download(
                repo_id=ds, 
                repo_type="dataset",
                local_dir=os.path.join(hf_dir, ds.split('/')[-1]),
                resume_download=True,
                ignore_patterns=["*.msgpack", "*.h5"] # Agir binaryleri atla
            )
        except Exception as e:
            print(f"  [!] HATA {ds}: {e}")

def download_kaggle(base_dir):
    print(f"\n[{len(KAGGLE_DATASETS)}] Kaggle dataseti indiriliyor...")
    kg_dir = os.path.join(base_dir, "kaggle")
    os.makedirs(kg_dir, exist_ok=True)
    
    try:
        import kaggle
    except ImportError:
        print("  [!] HATA: kaggle paketi yuklu degil. 'pip install kaggle' calistirin ve ~/.kaggle/kaggle.json ayarlayin.")
        return

    for ds in KAGGLE_DATASETS:
         print(f"  Downloading -> {ds}")
         dest = os.path.join(kg_dir, ds.split('/')[-1])
         try:
             if 'c/' in ds:
                 comp = ds.split('/')[-1]
                 kaggle.api.competition_download_files(comp, path=dest, quiet=False)
             else:
                 kaggle.api.dataset_download_files(ds, path=dest, unzip=True, quiet=False)
         except Exception as e:
             print(f"  [!] HATA {ds}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Download all 104 datasets from compass artifact to raw directory")
    parser.add_argument("--data-dir", default="/workspace/data/raw", help="H200 uyumlu ana hedef klasoru")
    parser.add_argument("--skip-hf", action="store_true")
    parser.add_argument("--skip-kaggle", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.data_dir, exist_ok=True)

    # Indirme oncesi bilgi
    print("=================================================================")
    print("ULTIMATE SALES & MARKETING DATASET MATKABI (RAW INGESTION)")
    print("Amac     : Compass listesindeki tamami 100+ datasetin cekilmesi")
    print(f"Hedef Dir: {args.data_dir}")
    print("=================================================================")

    if not args.skip_hf:
        download_hf(args.data_dir)
        
    if not args.skip_kaggle:
         download_kaggle(args.data_dir)
         
    print("\nTum indirmeler tamamlandi. Siradaki adim 'filter_and_convert.py' olmalidir.")

if __name__ == "__main__":
    main()
