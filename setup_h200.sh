#!/bin/bash
# =============================================================================
# setup_h200.sh — H200 Sunucusu Kurulum Scripti
# =============================================================================
# Kullanim: bash setup_h200.sh
# Kaggle key'ini cevresel degisken olarak ver ya da scripti duzenle.
# =============================================================================

set -e  # Hata olursa dur

echo "=================================================="
echo " H200 Fine-Tune Ortami Kurulumu"
echo "=================================================="

# ── 1. Python paketleri ───────────────────────────────────────────────────────
echo ""
echo "[1/6] Python bagimliliklar kuruluyor..."
pip install -q --upgrade pip
pip install -q unsloth trl datasets peft transformers accelerate bitsandbytes \
               kaggle tqdm pyyaml huggingface_hub

echo "  OK: Paketler kuruldu."

# ── 2. Klasör yapısı ──────────────────────────────────────────────────────────
echo ""
echo "[2/6] Klasörler olusturuluyor..."
mkdir -p /workspace/models/tmp
mkdir -p /workspace/data/kaggle
mkdir -p /workspace/output/satis-reklam-ai
mkdir -p ~/.kaggle

echo "  OK: Klasörler hazır."

# ── 3. Kaggle API key ─────────────────────────────────────────────────────────
echo ""
echo "[3/6] Kaggle API key ayarlaniyor..."

# Key'i environment variable'dan al (ya da asagıya yaz)
KAGGLE_USERNAME="${KAGGLE_USERNAME:-emreocak}"
KAGGLE_KEY="${KAGGLE_KEY:-KGAT_5894ebabc67fd99947b36891ae7ed8d8}"

echo "{\"username\":\"${KAGGLE_USERNAME}\",\"key\":\"${KAGGLE_KEY}\"}" > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json

echo "  OK: Kaggle API hazır (user: ${KAGGLE_USERNAME})"

# ── 4. Qwen3-VL modeli ───────────────────────────────────────────────────────
echo ""
echo "[4/6] Qwen3-VL-8B-Thinking modeli indiriliyor..."
echo "  (Bu ~15-20 dakika surebilir)"

pip install -q "huggingface_hub[cli]"

python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    'Qwen/Qwen3-VL-8B-Thinking',
    local_dir='/workspace/models/Qwen3-VL-8B-Thinking',
    ignore_patterns=['*.msgpack', '*.h5']
)
print('Model indirildi.')
"

echo "  OK: Model indirildi."

# ── 5. Config path guncelle ──────────────────────────────────────────────────
echo ""
echo "[5/6] Config dosyası guncelleniyor..."

sed -i 's|E:/projectfinetune/models|/workspace/models|g' /workspace/configs/finetune_config.yaml
sed -i 's|./output/|/workspace/output/|g' /workspace/configs/finetune_config.yaml

echo "  OK: Config güncellendi."

# ── 6. Kaggle datasetleri ────────────────────────────────────────────────────
echo ""
echo "[6/7] Kaggle metin datasetleri indiriliyor ve donusturuluyor..."
python /workspace/scripts/download_kaggle_datasets.py

echo ""
echo "[7/7] Tablosal Kaggle datasetleri indiriliyor ve donusturuluyor..."
python /workspace/scripts/convert_tabular_datasets.py

echo ""
echo "=================================================="
echo " KURULUM TAMAMLANDI!"
echo "=================================================="
echo ""
echo " Egitimi baslatmak icin:"
echo "   python /workspace/scripts/finetune.py"
echo ""
echo " Sadece HF dataseti ile (Kaggle olmadan):"
echo "   python /workspace/scripts/finetune.py"
echo ""
echo " Onceden hazırlanmis dosya ile:"
echo "   python /workspace/scripts/finetune.py --from-file /workspace/models/tmp/training_data.jsonl"
echo "=================================================="
