"""
Inference Script — Fine-Tuned Qwen3-VL-8B-Thinking
===================================================
Fine-tune edilmiş modeli test et.
Text ve görsel (image) sorgularını destekler.
"""

import os

# HF cache'i D: sürücüsüne yönlendir (C: dolu)
os.environ["HF_HOME"] = "D:\\hf_cache"
os.environ["TRANSFORMERS_CACHE"] = "D:\\hf_cache"

import json
import argparse
from pathlib import Path


def load_model(model_path: str, base_model: str = "Qwen/Qwen3-VL-8B-Thinking"):
    """Fine-tune edilmiş modeli yükle."""
    from unsloth import FastVisionModel

    print(f"📦 Model yükleniyor: {model_path}")

    model, tokenizer = FastVisionModel.from_pretrained(
        model_name=model_path if os.path.exists(model_path) else base_model,
        max_seq_length=4096,
        load_in_4bit=True,
    )

    # Inference modu
    FastVisionModel.for_inference(model)

    print("✅ Model hazır!")
    return model, tokenizer


def run_text_query(model, tokenizer, query: str, system_prompt: str = None):
    """Sadece metin sorgusu çalıştır."""
    if system_prompt is None:
        system_prompt = """Sen bir satış psikolojisi ve dijital reklam stratejisi uzmanısın.
Türkiye ve global pazarları iyi bilirsin. Adım adım düşün ve muhakeme yap."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        temperature=0.6,
        top_p=0.9,
        do_sample=True,
    )

    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return response


def run_image_query(model, tokenizer, image_path: str, query: str, system_prompt: str = None):
    """Görsel + metin sorgusu çalıştır (VL özelliği)."""
    from PIL import Image

    if system_prompt is None:
        system_prompt = """Sen bir satış psikolojisi ve dijital reklam stratejisi uzmanısın.
Reklam görsellerini analiz edip stratejik öneriler sunarsın."""

    image = Image.open(image_path).convert("RGB")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": query},
        ]},
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    # Qwen VL processor kullanımı
    from qwen_vl_utils import process_vision_info
    image_inputs, video_inputs = process_vision_info(messages)

    inputs = tokenizer(
        text,
        images=image_inputs,
        videos=video_inputs,
        return_tensors="pt",
        padding=True,
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        temperature=0.6,
        top_p=0.9,
        do_sample=True,
    )

    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return response


def interactive_mode(model, tokenizer):
    """İnteraktif sohbet modu."""
    print("\n" + "=" * 60)
    print("  🎯 Satış & Reklam AI — İnteraktif Mod")
    print("  Komutlar:")
    print("    /image <dosya_yolu> — Görsel analiz modu")
    print("    /quit               — Çıkış")
    print("=" * 60 + "\n")

    while True:
        try:
            query = input("📝 Sen: ").strip()

            if not query:
                continue
            if query.lower() in ["/quit", "/exit", "/q"]:
                print("👋 Görüşmek üzere!")
                break

            # Görsel sorgulama
            if query.startswith("/image"):
                parts = query.split(maxsplit=1)
                if len(parts) < 2:
                    print("⚠️  Kullanım: /image dosya_yolu.jpg Sorunuz")
                    continue

                remaining = parts[1].strip()
                # İlk kelime dosya yolu, gerisi soru
                path_and_query = remaining.split(maxsplit=1)
                image_path = path_and_query[0]
                img_query = path_and_query[1] if len(path_and_query) > 1 else "Bu reklam görselini analiz et."

                if not os.path.exists(image_path):
                    print(f"❌ Dosya bulunamadı: {image_path}")
                    continue

                print("🔍 Görsel analiz ediliyor...")
                response = run_image_query(model, tokenizer, image_path, img_query)
            else:
                print("🧠 Düşünüyorum...")
                response = run_text_query(model, tokenizer, query)

            print(f"\n🤖 AI: {response}\n")

        except KeyboardInterrupt:
            print("\n👋 Görüşmek üzere!")
            break


def run_benchmark(model, tokenizer):
    """Örnek sorgularla benchmark testi."""
    test_queries = [
        {
            "category": "Meta Ads Analizi",
            "query": """Bu Meta Ads kampanya verilerini analiz et ve öneriler sun:

Kampanya: E-ticaret ayakkabı satışı
Platform: Facebook + Instagram
Bütçe: Günlük 500 TL
Hedef Kitle: 18-65, Türkiye geneli
Gösterim: 45,000
Tıklama: 320
CTR: 0.71%
CPC: 1.56 TL
Dönüşüm: 8
CPA: 62.50 TL
ROAS: 2.1"""
        },
        {
            "category": "Satış Psikolojisi",
            "query": "Bir müşteri 'Çok pahalı' dediğinde hangi ikna tekniklerini kullanmalıyım? Türkiye pazarı için somut örneklerle açıkla."
        },
        {
            "category": "Reklam Metni Analizi",
            "query": """Bu reklam metnini satış psikolojisi açısından analiz et ve iyileştir:

"Harika ürünlerimize göz atın! Kaliteli ve uygun fiyatlı ürünlerimiz sizleri bekliyor. Hemen alışverişe başlayın!"
"""
        },
        {
            "category": "Google Ads Stratejisi",
            "query": "Google Ads'te Quality Score 4/10. Anahtar kelimeler: 'koşu ayakkabısı', 'spor ayakkabı online'. CPC çok yüksek çıkıyor. Ne yapmalıyım?"
        },
        {
            "category": "A/B Test Yorumlama",
            "query": """İki reklam varyantı test ettim:

Varyant A (Kontrol): CTR %1.2, CPA 45 TL, ROAS 3.1
Varyant B (Yeni hook): CTR %1.8, CPA 38 TL, ROAS 3.6
Örneklem: Her biri 5,000 gösterim

Bu sonuçları yorumla ve stratejik tavsiyelerde bulun."""
        },
    ]

    print("\n" + "=" * 60)
    print("  📊 BENCHMARK TESTİ")
    print("=" * 60)

    results = []
    for i, test in enumerate(test_queries):
        print(f"\n--- Test {i+1}/{len(test_queries)}: {test['category']} ---")
        print(f"Soru: {test['query'][:100]}...")

        import time
        start = time.time()
        response = run_text_query(model, tokenizer, test["query"])
        elapsed = time.time() - start

        print(f"Süre: {elapsed:.1f}s")
        print(f"Cevap uzunluğu: {len(response)} karakter")
        print(f"Cevap (ilk 300 karakter): {response[:300]}...")

        results.append({
            "category": test["category"],
            "query": test["query"],
            "response": response,
            "elapsed_seconds": elapsed,
            "response_length": len(response),
        })

    # Sonuçları kaydet
    output_file = Path("./output/benchmark_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Benchmark sonuçları kaydedildi: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Fine-tuned model inference")
    parser.add_argument("--model-path", type=str, default="./output/satis-reklam-ai/final",
                        help="Fine-tune edilmiş model dizini")
    parser.add_argument("--base-model", type=str, default="Qwen/Qwen3-VL-8B-Thinking",
                        help="Base model (fine-tune edilmemişse)")
    parser.add_argument("--mode", type=str, default="interactive",
                        choices=["interactive", "benchmark", "single"],
                        help="Çalışma modu")
    parser.add_argument("--query", type=str, default=None,
                        help="Tek sorgu (mode=single)")
    parser.add_argument("--image", type=str, default=None,
                        help="Görsel dosya yolu (opsiyonel)")
    args = parser.parse_args()

    model, tokenizer = load_model(args.model_path, args.base_model)

    if args.mode == "interactive":
        interactive_mode(model, tokenizer)
    elif args.mode == "benchmark":
        run_benchmark(model, tokenizer)
    elif args.mode == "single":
        if not args.query:
            print("❌ --query argümanı gerekli")
            return
        if args.image:
            response = run_image_query(model, tokenizer, args.image, args.query)
        else:
            response = run_text_query(model, tokenizer, args.query)
        print(f"\n🤖 AI:\n{response}")


if __name__ == "__main__":
    main()
