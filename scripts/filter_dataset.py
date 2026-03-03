"""
filter_dataset.py — Quality Filter + Think Tag Injector
=========================================================
168M satirlik training_data.jsonl'i basan sona gecer.
- Dusuk kaliteli satirlari eler
- <think> tag'i eksik olan assistant yanitlarina ekler
- Kalanlarin HEPSINI yeni dosyaya yazar (limit yok)

Kullanim:
    python scripts/filter_dataset.py
    python scripts/filter_dataset.py --input X --output Y
"""

import json
import sys
import re
import argparse
from tqdm import tqdm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# FILTRE KURALLARI
MIN_CHARS = 200     # Cok kisa satirlari at
MAX_CHARS = 20000   # Cok uzun satirlari at

# Kalite sinyalleri — bunlari iceren satirlari dogrudan at
JUNK_PATTERNS = [
    "[GENERATION_ERROR",
    "UnicodeDecodeError",
    "Traceback (most recent",
]

# <think> olmayan yanit icin minimum uzunluk (cok kisa yanit = dandik veri)
MIN_ASSISTANT_RESPONSE = 80


def extract_assistant_block(text: str) -> tuple[str, str, str]:
    """
    Qwen chat template formatindan assistant yanitini bul.
    Returns: (before_assistant, assistant_content, after)
    Format: <|im_start|>assistant\n...<|im_end|>
    """
    marker = "<|im_start|>assistant\n"
    end_marker = "<|im_end|>"

    start_idx = text.rfind(marker)  # Son asistan blogu
    if start_idx == -1:
        return text, "", ""

    content_start = start_idx + len(marker)
    end_idx = text.find(end_marker, content_start)
    if end_idx == -1:
        return text[:start_idx + len(marker)], text[content_start:], ""

    before = text[:start_idx + len(marker)]
    content = text[content_start:end_idx]
    after = text[end_idx:]
    return before, content, after


def inject_think(content: str) -> str:
    """
    <think> tag'i yoksa ekle.
    Kisa ama anlamli bir thinking section olustur.
    """
    if "<think>" in content and "</think>" in content:
        return content  # Zaten var

    # Yaniti analiz et ve uygun think ekle
    content_preview = content[:150].replace("\n", " ").strip()
    think_block = f"<think>\nYaniti dikkatlice olusturuyorum.\nKonu: {content_preview[:100]}\n</think>\n\n"
    return think_block + content


def is_quality(text: str, assistant_content: str) -> tuple[bool, str]:
    """True: kal, False + neden: ele."""

    # 1. Uzunluk
    if len(text) < MIN_CHARS:
        return False, "too_short"
    if len(text) > MAX_CHARS:
        return False, "too_long"

    # 2. Junk pattern
    for pat in JUNK_PATTERNS:
        if pat in text:
            return False, "junk_pattern"

    # 3. Assistant yaniti yeterince uzun mu?
    clean_content = assistant_content.replace("<think>", "").replace("</think>", "").strip()
    if len(clean_content) < MIN_ASSISTANT_RESPONSE:
        return False, "empty_response"

    return True, "ok"


def filter_and_fix_file(input_file: str, output_file: str):
    stats = {
        "total": 0,
        "kept": 0,
        "injected_think": 0,
        "json_error": 0,
        "too_short": 0,
        "too_long": 0,
        "junk_pattern": 0,
        "empty_response": 0,
        "no_assistant": 0,
    }

    print(f"Filtreleme + Think Injection baslaniyor")
    print(f"  Kaynak: {input_file}")
    print(f"  Hedef:  {output_file}")
    print()

    with open(input_file, 'r', encoding='utf-8', errors='replace') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:

        pbar = tqdm(f_in, desc="Processing", unit=" lines", mininterval=3.0)

        for line in pbar:
            stats["total"] += 1
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                stats["json_error"] += 1
                continue

            text = data.get("text", "")
            if not isinstance(text, str):
                stats["json_error"] += 1
                continue

            # Assistant blogunu bul
            before, assistant_content, after = extract_assistant_block(text)

            if not assistant_content:
                stats["no_assistant"] += 1
                continue

            # Kalite kontrolu (think inject'ten once)
            ok, reason = is_quality(text, assistant_content)
            if not ok:
                stats[reason] = stats.get(reason, 0) + 1
                continue

            # <think> yoksa ekle
            fixed_content = inject_think(assistant_content)
            if fixed_content != assistant_content:
                stats["injected_think"] += 1
                text = before + fixed_content + after
                data["text"] = text

            f_out.write(json.dumps(data, ensure_ascii=False) + "\n")
            stats["kept"] += 1

            # Progress gostergesi
            if stats["total"] % 1000000 == 0:
                pbar.set_postfix({
                    "kept": f"{stats['kept']:,}",
                    "think_inj": f"{stats['injected_think']:,}",
                    "kept%": f"{stats['kept']/stats['total']*100:.1f}%",
                })

    total = stats["total"]
    kept = stats["kept"]
    elim = total - kept

    print()
    print("=" * 55)
    print("OZET")
    print("=" * 55)
    print(f"Toplam incelenen:        {total:>15,}")
    print(f"Kaliteli (KALDI):        {kept:>15,}  ({kept/total*100:.1f}%)")
    print(f"Think tag eklendi:       {stats['injected_think']:>15,}  ({stats['injected_think']/max(kept,1)*100:.1f}% of kept)")
    print(f"Elenen toplam:           {elim:>15,}  ({elim/total*100:.1f}%)")
    print()
    print("Eleme nedenleri:")
    for r in ["too_short", "too_long", "junk_pattern", "empty_response", "no_assistant", "json_error"]:
        v = stats.get(r, 0)
        if v > 0:
            print(f"  {r:25s} {v:>12,}  ({v/total*100:.1f}%)")

    print()
    print(f"Temiz dosya: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  default="E:/projectfinetune/models/tmp/training_data.jsonl")
    parser.add_argument("--output", default="E:/projectfinetune/models/tmp/training_data_clean.jsonl")
    args = parser.parse_args()

    filter_and_fix_file(args.input, args.output)
