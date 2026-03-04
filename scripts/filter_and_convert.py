"""
filter_and_convert.py
=====================
download_all_raw_datasets.py tarafindan indirilen TUM (104 adet) dataseti 
raw klasorlerinden okur.

Islevi:
1. Gecersiz, null, cok kisa satirlari reddeder.
2. Tablosal, metin, diyalog, Q&A yapilarini otomatik tarar ve Qwen3-VL
   Thinking formatina (system, user, assistant<think>) donusturur.
3. Egitime hazir temiz bir train.jsonl cikarir.
"""

import os
import sys
import json
import csv
import glob
import random
from pathlib import Path
from tqdm import tqdm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAW_DIR = "/workspace/data/raw"
OUTPUT_FILE = "/workspace/models/tmp/filtered_train.jsonl"

SYSTEM_PROMPT = """Sen dunya capinda bir satis, pazarlama, kopyazarlik ve ikna uzmanisin.
Verilen metinleri, kullanici davranislarini veya kampanya metriklerini analiz eder;
etkileyici satirlar cikarir veya stratejik optimizasyon onerileri sunarsin."""

# -------------------------------------------------------------------------
# Yardimci Fonksiyonlar
# -------------------------------------------------------------------------
def is_valid_text(txt):
    if not txt or not isinstance(txt, str): return False
    txt = txt.strip()
    return len(txt) > 20 and txt.lower() not in ["none", "nan", "null", "unknown"]

def think(instruction: str, insight: str) -> str:
    preview = instruction[:150].replace("\n", " ").strip()
    return (
        f"<think>\n"
        f"Durumu analiz ediyorum: {preview}...\n"
        f"Kullaniciya yonelik stratejik, yaratici ve dogrudan bir yanit tasarliyorum.\n"
        f"</think>\n\n"
        f"{insight}"
    )

def make_ex(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": user[:4000].strip()},
            {"role": "assistant", "content": think(user, assistant[:4000].strip())},
        ]
    }

# -------------------------------------------------------------------------
# Auto-Discovery: CSV / JSON / Parquet / JSONL okuyucu
# -------------------------------------------------------------------------

def process_generic_tabular_row(row: dict) -> dict:
    """Tablosal bir satiri basitce formatlar, eger ozellesmis bir analyzer yoksa fallback olarak calisir."""
    # Ozellikle "text", "review", "description", "headline", "body", "content" vs var mi bak
    keys_lower = {k.lower(): k for k in row.keys()}
    
    # 1. Acik Metin (Text, Review, Headline) varsa -> Analiz iste
    text_keys = ["text", "review", "headline", "description", "body", "content", "message", "tweet", "comment"]
    found_text_key = next((keys_lower[k] for k in text_keys if k in keys_lower), None)
    
    if found_text_key and is_valid_text(row[found_text_key]):
        text_val = row[found_text_key]
        
        # Etiket/skor var mi bak (label, sentiment, score, rating, clickbait, churn vb.)
        label_keys = ["label", "sentiment", "score", "rating", "clickbait", "churn", "target", "converted"]
        found_label_key = next((keys_lower[k] for k in label_keys if k in keys_lower), None)
        
        if found_label_key:
            label_val = row[found_label_key]
            u = f"Bu metni/icerigi pazarlama acisindan analiz et: \n\n\"{text_val}\""
            a = f"Degerlendirme Sonucu: {label_val}\n\nBu tarz bir icerik izleyicide/musteride yukaridaki etkiyi/kategoriyi tetikleme egilimindedir."
            return make_ex(u, a)
        else:
            # Sadece metin varsa (ornegin urun aciklamasi), reklam kopyasi yazdirmaya zorla
            u = f"Asagidaki bilgiye dayanarak carpici bir reklam basligi ve kisa aciklamasi yaz:\n\n{text_val}"
            a = f"Baslik: {text_val[:30].strip()}...\nSpot: Bu detaylara sahip urun/hizmet ile hedef kitleye dogrudan temas et.\n(Aciklama bazli uretildigi icin asil yaratici kopyayi senin stratejine birakiyorum.)"
            return make_ex(u, a)

    # 2. Eger Q&A yapisi ise
    if "question" in keys_lower and "answer" in keys_lower:
        q = row[keys_lower["question"]]
        a = row[keys_lower["answer"]]
        if is_valid_text(q) and is_valid_text(a):
            return make_ex(q, a)

    if "instruction" in keys_lower and "output" in keys_lower:
        q = row[keys_lower["instruction"]]
        a = row[keys_lower["output"]]
        if is_valid_text(q) and is_valid_text(a):
            return make_ex(q, a)

    # 3. Bilindik tablo kolonlari (kampanya, metrikler vs)
    if "clicks" in keys_lower or "spend" in keys_lower or "revenue" in keys_lower or "impressions" in keys_lower:
        # Tablosal reklam verisi
        summary = ", ".join([f"{k}: {v}" for k, v in row.items() if v and str(v).lower() not in ["none", "nan", ""]])
        if len(summary) > 20:
             u = f"Bu reklam/kampanya tablosunu analiz et ve optimize et:\n{summary}"
             a = f"Veriler incelendiginde (or: {summary[:100]}), bu tur kampanyalarda ROI/CTR artisi saglamak icin en cok harcama getiren -ya da donusum saglayan- kanala agirlik verilmeli, A/B testi uygulanmalidir."
             return make_ex(u, a)

    return None # Anlamli bir sey cikarilamadi

def process_file(file_path: str, out_f) -> int:
    count = 0
    ext = os.path.splitext(file_path)[-1].lower()
    
    try:
        if ext == '.csv':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ex = process_generic_tabular_row(row)
                    if ex:
                        out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                        count += 1
                        
        elif ext == '.jsonl':
             with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                  for str_line in f:
                       try:
                           row = json.loads(str_line)
                           if isinstance(row, dict):
                               ex = process_generic_tabular_row(row)
                               if ex:
                                   out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                                   count += 1
                       except json.JSONDecodeError:
                           pass
                           
        elif ext == '.json':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for row in data:
                        if isinstance(row, dict):
                            ex = process_generic_tabular_row(row)
                            if ex:
                                out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                                count += 1
        
        # Parquet, Arrow, vs HF tarafindan direkt datsets cacheine alindigi icin klasor icini tararken atliyoruz, 
        # onlari asagida load_dataset ile process edecegiz eger HF ise. Kaggle'dan baska bir sey geldiyse pandas gerekir, basitlik adina atliyoruz.
        
    except Exception as e:
        print(f"    [!] Error reading {file_path}: {e}")
        
    return count

def process_hf_parquet(dataset_dir: str, out_f) -> int:
    """HuggingFace reposundan inen parquet/arrow dosyalarini datasets kutuphanesi ile okur"""
    count = 0
    from datasets import load_dataset
    try:
        # Klasor icindeki .parquet dosyalarini yuklemeye calis
        parquet_files = glob.glob(os.path.join(dataset_dir, "**/*.parquet"), recursive=True)
        if not parquet_files:
            return 0
            
        ds = load_dataset("parquet", data_files=parquet_files, split="train")
        for row in tqdm(ds, desc=f"  {os.path.basename(dataset_dir)}", leave=False):
             ex = process_generic_tabular_row(row)
             if ex:
                 out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                 count += 1
    except Exception as e:
        print(f"    [!] HF Parquet okuma hatasi {dataset_dir}: {e}")
    return count


def main():
    if not os.path.exists(RAW_DIR):
        print(f"HATA: {RAW_DIR} bulunamadi. Once download_all_raw_datasets.py calistirilmalidir.")
        return

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    total = 0
    print(f"======== FITRELEME VE DONUSTURME BASLIYOR ========")
    print(f"Kaynak: {RAW_DIR}")
    print(f"Hedef:  {OUTPUT_FILE}")
    print(f"==================================================\n")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        
        # 1. Kaggle Klasorlerini Tara (Genelde CSV/JSON)
        kaggle_dir = os.path.join(RAW_DIR, "kaggle")
        if os.path.exists(kaggle_dir):
            print("\n[KAGGLE KLASORLERI TARANIYOR]")
            for root, dirs, files in os.walk(kaggle_dir):
                for file in files:
                    if file.endswith(('.csv', '.json', '.jsonl')):
                        fpath = os.path.join(root, file)
                        print(f"  Isleme aliniyor: {fpath}")
                        c = process_file(fpath, out_f)
                        total += c
                        print(f"    -> {c:,} gecerli formatta ornek cikarildi.")

        # 2. HF Klasorlerini Tara (Genelde Parquet/JSONL)
        hf_dir = os.path.join(RAW_DIR, "hf")
        if os.path.exists(hf_dir):
            print("\n[HUGGINGFACE KLASORLERI TARANIYOR]")
            # Her HF repo bir klasor altindadir
            for repo_folder in os.listdir(hf_dir):
                repo_path = os.path.join(hf_dir, repo_folder)
                if os.path.isdir(repo_path):
                     print(f"  Isleme aliniyor HF Repo: {repo_folder}")
                     
                     # Once flat json/jsonl/csv var mi
                     local_c = 0
                     for f in glob.glob(os.path.join(repo_path, "**/*.*"), recursive=True):
                         if f.endswith(('.csv', '.json', '.jsonl')):
                             local_c += process_file(f, out_f)
                             
                     # Sonra varsa parquetleri toplica hallet
                     parquet_c = process_hf_parquet(repo_path, out_f)
                     
                     c = local_c + parquet_c
                     total += c
                     print(f"    -> {c:,} gecerli formatta ornek cikarildi.")

    print(f"\n==================================================")
    print(f"TAMAMLANDI!")
    print(f"Toplam Gecerli Ornek: {total:,}")
    print(f"Cikti Dosyasi: {OUTPUT_FILE}")
    print(f"==================================================")
    print("Egtime baslamak uzere 'finetune.py --from-file /workspace/models/tmp/filtered_train.jsonl' kullanilabilir.")

if __name__ == "__main__":
    main()
