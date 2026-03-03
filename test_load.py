import os
import sys

# Windows terminal Unicode fix
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import logging
logging.basicConfig(level=logging.INFO)

print("Imports basliyor...")
from unsloth import FastVisionModel
import torch
print("Imports bitti. CUDA:", torch.cuda.is_available())

model_name = "E:/projectfinetune/models/Qwen3-VL-8B-Thinking"

print(f"Model yukleniyor: {model_name}")
try:
    model, tokenizer = FastVisionModel.from_pretrained(
        model_name=model_name,
        max_seq_length=4096,
        load_in_4bit=True,
        dtype=None,
    )
    print("Model basariyla yuklendi!")
except Exception as e:
    import traceback
    traceback.print_exc()
