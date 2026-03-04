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
    if not txt: return False
    if not isinstance(txt, str):
        try:
            txt = str(txt)
        except:
            return False
    txt = txt.strip()
    return len(txt) >= 2 and txt.lower() not in ["none", "nan", "null", "unknown", "[]", "{}"]

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
            {"role": "user",      "content": str(user)[:4000].strip()},
            {"role": "assistant", "content": think(str(user), str(assistant)[:4000].strip())},
        ]
    }

# -------------------------------------------------------------------------
# Auto-Discovery: CSV / JSON / Parquet / JSONL okuyucu
# -------------------------------------------------------------------------

def process_generic_tabular_row(row: dict) -> dict:
    """Tablosal, metin veya sohbet formatindaki satir objesini Qwen3-VL formatina donusturur."""
    keys_lower = {str(k).lower(): k for k in row.keys()}
    
    # 1. Sohbet / Mesaj Formati (messages, conversations)
    msg_keys = ["messages", "conversations", "dialogue", "chat"]
    found_msg = next((keys_lower[k] for k in msg_keys if k in keys_lower), None)
    if found_msg and isinstance(row[found_msg], list) and len(row[found_msg]) > 0:
        msgs = row[found_msg]
        user_text, assistant_text = "", ""
        for m in msgs:
            if isinstance(m, dict):
                role = str(m.get("role", m.get("from", ""))).lower()
                val = str(m.get("content", m.get("value", m.get("text", ""))))
                if role in ["user", "human", "client", "customer"]:
                    user_text += val + "\n"
                elif role in ["assistant", "gpt", "bot", "agent", "system"]:
                    assistant_text += val + "\n"
        if is_valid_text(user_text) and is_valid_text(assistant_text):
            return make_ex(user_text, assistant_text)

    # 2. Soru-Cevap veya Instruction-Output Formati
    q_keys = ["instruction", "question", "prompt", "query", "input"]
    a_keys = ["output", "answer", "response", "completion", "target"]
    found_q = next((keys_lower[k] for k in q_keys if k in keys_lower), None)
    found_a = next((keys_lower[k] for k in a_keys if k in keys_lower), None)
    
    if found_q and found_a:
        q = row[found_q]
        a = row[found_a]
        # Eger instruction ve input ayriysa birlestir
        if found_q == keys_lower.get("instruction") and "input" in keys_lower:
            inp = row[keys_lower["input"]]
            if is_valid_text(inp):
                q = f"{q}\n\nDetay/Baglam:\n{inp}"
                
        if is_valid_text(q) and is_valid_text(a):
            return make_ex(str(q), str(a))

    # 3. Metin + Etiket Formati (Review, Slogan, Tweet vb.)
    text_keys = ["text", "review", "headline", "description", "body", "content", "message", "tweet", "comment", "title", "slogan"]
    found_text = next((keys_lower[k] for k in text_keys if k in keys_lower), None)
    
    if found_text and is_valid_text(row[found_text]):
        text_val = row[found_text]
        label_keys = ["label", "sentiment", "score", "rating", "clickbait", "churn", "converted", "category", "topic", "class"]
        found_label = next((keys_lower[k] for k in label_keys if k in keys_lower), None)
        
        if found_label and is_valid_text(row[found_label]):
            label_val = row[found_label]
            u = f"Asagidaki metni/icerigi analiz ederek pazarlama/satis etkisini degerlendir:\n\n\"{text_val}\""
            a = f"Analiz/Etiket: {label_val}\n\nBu tur icerikler, bahsedilen kategoride tepki olusturma potansiyeline sahiptir."
            return make_ex(u, a)
        else:
            u = f"Gelen veriyi kullanarak carpici bir reklam/pazarlama konsepti cikar:\n\n{text_val}"
            a = f"Konsept Odagi: {str(text_val)[:50].strip()}...\n\nBu metnin temel mesajina uygun bir kanca (hook) kurgusu ile kitleye dogrudan temas edilmelidir."
            return make_ex(u, a)

    # 5. ULTIMATE CATCH-ALL Fallback
    valid_items = {k: v for k, v in row.items() if v is not None and str(v).strip().lower() not in ["none", "nan", "", "null"]}
    if len(valid_items) > 0:
        summary = ", ".join([f"{k}: {str(v)[:100]}" for k, v in list(valid_items.items())[:15]])
        u = f"Bu sistem veya e-ticaret verisini yorumlayip bir pazarlama cikarimi veya metrik analizi yap:\n{summary}"
        a = f"Veriler ({summary[:40]}...) baz alindiginda, satis performansini artirmak icin musteri gruplamasi, hedef kitlesel A/B testleri veya crm revizyonlari gibi satissal reaksiyonlar hedeflenebilir."
        return make_ex(u, a)

    return None # Anlamli bir format bulunamadi

def process_file(file_path: str, out_f, max_samples: int = 1000000) -> int:
    count = 0
    ext = os.path.splitext(file_path)[-1].lower()
    
    try:
        if ext == '.csv':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                all_rows = list(reader)
                if len(all_rows) > max_samples:
                    all_rows = all_rows[-max_samples:]
                    
                for row in all_rows:
                    ex = process_generic_tabular_row(row)
                    if ex:
                        out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                        count += 1
                        
        elif ext == '.jsonl':
             with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                  lines = f.readlines()
                  if len(lines) > max_samples:
                      lines = lines[-max_samples:]
                      
                  for str_line in lines:
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
            content_list = []
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        content_list = data
                    elif isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, list):
                                content_list.extend(v)
            except json.JSONDecodeError:
                # Kaggle JSON'larinin cogu hatali olarak jsonl formatina sahip
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        try:
                            content_list.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            
            if len(content_list) > max_samples:
                content_list = content_list[-max_samples:]
                
            for row in content_list:
                if isinstance(row, dict):
                    ex = process_generic_tabular_row(row)
                    if ex:
                        try:
                            out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")
                            count += 1
                        except Exception:
                            pass

        
        # Parquet, Arrow, vs HF tarafindan direkt datsets cacheine alindigi icin klasor icini tararken atliyoruz, 
        # onlari asagida load_dataset ile process edecegiz eger HF ise. Kaggle'dan baska bir sey geldiyse pandas gerekir, basitlik adina atliyoruz.
        
    except Exception as e:
        print(f"    [!] Error reading {file_path}: {e}")
        
    return count

def process_hf_parquet(dataset_dir: str, out_f, max_samples: int = 1000000) -> int:
    """HuggingFace reposundan inen parquet/arrow dosyalarini datasets kutuphanesi ile okur"""
    count = 0
    from datasets import load_dataset
    try:
        # Klasor icindeki .parquet dosyalarini yuklemeye calis
        parquet_files = glob.glob(os.path.join(dataset_dir, "**/*.parquet"), recursive=True)
        if not parquet_files:
            return 0
            
        ds = load_dataset("parquet", data_files=parquet_files, split="train")
        
        # Guncel veriyi almak adina son siradaki elemanlari seciyoruz:
        if len(ds) > max_samples:
            ds = ds.select(range(len(ds) - max_samples, len(ds)))
            
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
                        c = process_file(fpath, out_f)
                        total += c
                        print(f"  {file} -> {c:,} ornek")

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
                     print(f"  HF:{repo_folder} -> {c:,} ornek")

    print(f"\n==================================================")
    print(f"TAMAMLANDI!")
    print(f"Toplam Gecerli Ornek: {total:,}")
    print(f"Cikti Dosyasi: {OUTPUT_FILE}")
    print(f"==================================================")
    print("Egtime baslamak uzere 'finetune.py --from-file /workspace/models/tmp/filtered_train.jsonl' kullanilabilir.")

if __name__ == "__main__":
    main()
