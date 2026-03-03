"""Her 0-sample datasetin kolonlarini ve ilk satirini goster."""
from datasets import load_dataset

ZERO_DATASETS = [
    ("spawn99/PersuasionForGood", {"split": "FullDialog"}),
    ("smangrul/ad-copy-generation", {"split": "train"}),
    ("c-s-ale/Product-Descriptions-and-Ads", {"split": "train"}),
    ("suolyer/copywriting", {"split": "validation"}),
    ("philschmid/amazon-product-descriptions-vlm", {"split": "train"}),
]

for name, kw in ZERO_DATASETS:
    print(f"\n{'='*60}")
    print(f"DATASET: {name} (split={kw.get('split','train')})")
    try:
        ds = load_dataset(name, **kw)
        print(f"Kolonlar: {ds.column_names}")
        print(f"Satir sayisi: {len(ds)}")
        if len(ds) > 0:
            item = ds[0]
            for k, v in item.items():
                val_str = str(v)[:200]
                print(f"  {k}: {val_str}")
    except Exception as e:
        print(f"HATA: {e}")
