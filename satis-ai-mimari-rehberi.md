# Satış & Pazarlama AI Sistemi — Tam Mimari Rehberi

## Genel Bakış

Senin istediğin şey şu: Bir AI'a reklam dosyalarını yüklüyorsun, o da sana "CTR'ın düşük çünkü hedef kitle yanlış, bütçeyi 25-34 yaş grubuna kaydır, reklam metninde scarcity (kıtlık) psikolojisi kullan" gibi detaylı, stratejik analizler yapıyor.

Bunu tek başına fine-tuning ile yapamazsın. Üç katmanlı bir sistem lazım:

```
┌─────────────────────────────────────────────────────┐
│                    KULLANICI                         │
│         "Meta Ads Excel dosyamı analiz et"          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              AGENT / ORKESTRASYON                    │
│           (LangChain, LlamaIndex, veya              │
│            CrewAI ile yönetilen akış)                │
└──────┬──────────────┬───────────────┬───────────────┘
       │              │               │
       ▼              ▼               ▼
┌────────────┐ ┌─────────────┐ ┌──────────────┐
│ FINE-TUNED │ │  RAG SİSTEM │ │  TOOL / API  │
│    LLM     │ │  (Vektör DB)│ │   KATMANI    │
│            │ │             │ │              │
│ • Satış    │ │ • Sektör    │ │ • Excel oku  │
│   bilgisi  │ │   raporları │ │ • CSV parse  │
│ • Reklam   │ │ • Geçmiş    │ │ • Grafik çiz │
│   strateji │ │   kampanya  │ │ • Meta API   │
│ • İkna     │ │   verilerin │ │ • Google API │
│   tekniği  │ │ • Best      │ │ • Python çalı│
│ • Psikoloj │ │   practices │ │   ştır       │
└────────────┘ └─────────────┘ └──────────────┘
     BEYİN          HAFIZA         EL & GÖZ
```

---

## KATMAN 1: Fine-Tuned LLM (BEYİN)

### Ne işe yarar?

Modele "satış ve reklam uzmanı" kimliği kazandırır. Fine-tuning sonrası model şunları bilir:
- Bir CTR'ın iyi mi kötü mü olduğunu sektörel benchmark'larla değerlendirir
- Reklam metnini ikna psikolojisi açısından analiz eder
- Hedef kitle stratejisi önerir
- Bütçe dağılımı hakkında tavsiye verir

### Hangi base model?

| Model | Boyut | Avantaj | Dezavantaj |
|-------|-------|---------|------------|
| Llama 3.1 8B | 8B | Hızlı, ucuz, LoRA ile kolay | Daha az karmaşık analiz |
| Mistral 7B | 7B | İyi performans/boyut oranı | Türkçe desteği sınırlı |
| Llama 3.1 70B | 70B | Çok güçlü analiz | Pahalı, güçlü GPU gerekli |
| Qwen 2.5 72B | 72B | Çok dilli, güçlü | Yüksek donanım ihtiyacı |

**Öneri:** Başlangıç için **Llama 3.1 8B + QLoRA** ile başla. Ucuz ve hızlı. Sonuçlar yetersizse 70B'ye geç.

### Fine-tuning veri seti nasıl hazırlanır?

Önceki listeden topladığın ham veri setlerini doğrudan kullanamazsın. Bunları **instruction-tuning formatına** çevirmen gerek:

```json
{
  "instruction": "Bu Meta Ads kampanya verilerini analiz et ve öneriler sun.",
  "input": "Kampanya: E-ticaret ayakkabı satışı\nPlatform: Facebook + Instagram\nBütçe: Günlük 500 TL\nHedef Kitle: 18-65, Türkiye geneli\nGösterim: 45,000\nTıklama: 320\nCTR: 0.71%\nCPC: 1.56 TL\nDönüşüm: 8\nCPA: 62.50 TL\nROAS: 2.1",
  "output": "## Analiz Özeti\n\n**CTR (0.71%)** sektör ortalamasının (%0.90-1.2 e-ticaret) altında. Bu genellikle iki nedenden kaynaklanır:\n\n**1. Hedef Kitle Çok Geniş**\n18-65 yaş aralığı çok geniş. Ayakkabı satışında en aktif segment genellikle 22-38 yaş arasıdır. Öneri: Lookalike audience oluşturup yaş aralığını daralt.\n\n**2. Reklam Kreatifi/Metni**\nCTR düşüklüğü genellikle dikkat çekici olmayan görsel veya zayıf hook'tan kaynaklanır. Reklam metninde şu ikna tekniklerini dene:\n- **Scarcity (Kıtlık):** 'Son 50 çift' veya 'Bu fiyat sadece 48 saat'\n- **Social Proof:** 'Bu ay 2,300+ kişi bu modeli aldı'\n- **Loss Aversion:** 'Bu indirimi kaçırma'\n\n**ROAS (2.1)** karlılık sınırında. CPA'yı düşürmek için:\n- Retargeting kampanyası ekle (sepeti terk edenler)\n- Conversion API kurulumunu kontrol et\n- Broad targeting yerine interest-based segmentasyona geç"
}
```

### Veri seti oluşturma stratejisi

**Adım 1: Ham veri setlerini topla** (önceki 104 veri setinden ilgili olanları indir)

**Adım 2: Sentetik veri üret** — GPT-4 veya Claude'dan instruction formatında örnekler ürettir:

```
Senaryo türleri (her birinden 200-500 örnek):
├── Meta Ads kampanya analizi (düşük CTR, yüksek CPA, düşük ROAS senaryoları)
├── Google Ads kampanya analizi (Quality Score, anahtar kelime optimizasyonu)
├── Reklam metni analizi (ikna teknikleri, hook kalitesi, CTA değerlendirme)
├── Hedef kitle optimizasyonu (demografik, ilgi alanı, lookalike önerileri)
├── Bütçe dağılımı stratejisi (kanal bazlı, kampanya bazlı)
├── A/B test yorumlama (hangi varyant neden kazandı)
├── Satış psikolojisi danışmanlığı (fiyatlama, ikna, itiraz yönetimi)
├── Funnel analizi (TOFU/MOFU/BOFU optimizasyonu)
├── E-posta pazarlama stratejisi (konu satırı, gönderim zamanı, segmentasyon)
└── Genel dijital pazarlama stratejisi (çok kanallı planlama)
```

**Adım 3: Kalite kontrolü** — Her örneği manuel incele. Yanlış bilgi, tutarsız tavsiye, jenerik cevapları ele. Hedef: Minimum **2,000-5,000 kaliteli örnek.**

**Adım 4: Türkçe çeviri/uyarlama** — Eğer Türkçe bir model istiyorsan, örneklerin çoğunu Türkçeye çevir ve Türkiye pazarına uyarla (TL cinsinden bütçeler, Türk tüketici davranışları vs.)

### Fine-tuning teknik kurulum

```python
# QLoRA ile Llama 3.1 8B Fine-tuning
# Gereksinimler: 1x NVIDIA A100 40GB veya RTX 4090 24GB

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

# 1. Modeli 4-bit quantize ederek yükle
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# 2. LoRA konfigürasyonu
lora_config = LoraConfig(
    r=16,                      # Rank — 16 iyi bir başlangıç
    lora_alpha=32,             # Scaling factor
    target_modules=[           # Hangi katmanlar eğitilecek
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# 3. Veri setini yükle
dataset = load_dataset("json", data_files="sales_marketing_dataset.jsonl")

# 4. Chat template formatla
def format_chat(example):
    messages = [
        {"role": "system", "content": "Sen bir satış psikolojisi ve dijital reklam stratejisi uzmanısın."},
        {"role": "user", "content": f"{example['instruction']}\n\n{example['input']}"},
        {"role": "assistant", "content": example['output']}
    ]
    return {"text": tokenizer.apply_chat_template(messages, tokenize=False)}

dataset = dataset.map(format_chat)

# 5. Eğitim
training_args = SFTConfig(
    output_dir="./sales-marketing-llm",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    max_seq_length=4096,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)

trainer.train()

# 6. Modeli kaydet
model.save_pretrained("./sales-marketing-llm-final")
tokenizer.save_pretrained("./sales-marketing-llm-final")
```

### Fine-tuning alternatifleri (GPU yoksa)

| Platform | Fiyat | Kolaylık |
|----------|-------|----------|
| Google Colab Pro+ | ~50$/ay | Kolay, Jupyter notebook |
| RunPod | GPU başına saat ücret (~1-2$/saat) | Orta, Docker |
| Together AI | Fine-tuning API | Çok kolay, kod gerektirmez |
| OpenAI Fine-tuning | ~8$/1M token | En kolay ama sadece GPT modelleri |
| Hugging Face AutoTrain | Değişken | Arayüzden fine-tune |

---

## KATMAN 2: RAG Sistemi (HAFIZA)

### Ne işe yarar?

Model her şeyi ezbere bilemez. RAG ile modelin erişebildiği bir bilgi bankası oluşturursun. Model soru sorulduğunda önce bu bankadan ilgili bilgileri çeker, sonra cevap verir.

### RAG'a ne koyarsın?

```
Bilgi Bankası İçerikleri:
├── Sektör Raporları
│   ├── Meta Ads benchmark raporları (sektörel CTR, CPC, ROAS ortalamaları)
│   ├── Google Ads benchmark raporları
│   ├── E-ticaret dönüşüm oranı raporları
│   └── Dijital pazarlama trend raporları
│
├── Best Practice Dökümanları
│   ├── Meta Ads en iyi uygulamalar (resmi Meta dökümanları)
│   ├── Google Ads optimizasyon rehberleri
│   ├── Reklam kopyası yazım rehberleri
│   ├── Hedef kitle stratejileri
│   └── A/B test metodolojileri
│
├── Satış Psikolojisi Bilgi Tabanı
│   ├── Cialdini'nin 6 İkna Prensibi (detaylı açıklamalar + örnekler)
│   ├── AIDA, PAS, BAB, 4P frameworkleri
│   ├── Bilişsel önyargılar ve pazarlamada kullanımı
│   ├── Fiyatlama psikolojisi
│   └── Nöropazarlama prensipleri
│
├── Senin Geçmiş Verilerin
│   ├── Önceki kampanya raporları (ne işe yaradı, ne yaramadı)
│   ├── Müşteri segmentasyon verileri
│   ├── Başarılı reklam metinleri arşivi
│   └── Sektörel notların ve deneyimlerin
│
└── Güncel Bilgiler (periyodik güncelleme)
    ├── Platform algoritma değişiklikleri
    ├── Yeni reklam formatları
    └── Sektörel haberler
```

### RAG teknik kurulum

```python
# RAG Sistemi — ChromaDB + LangChain
# Bu kod bilgi bankasını oluşturur ve sorgulanabilir hale getirir

from langchain_community.document_loaders import (
    PyPDFLoader, CSVLoader, TextLoader, 
    UnstructuredExcelLoader, DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

# 1. Dökümanları yükle
def load_knowledge_base(directory_path):
    """Tüm dökümanları yükle: PDF, TXT, CSV, Excel"""
    loaders = {
        "**/*.pdf": PyPDFLoader,
        "**/*.txt": TextLoader,
        "**/*.csv": CSVLoader,
    }
    
    all_docs = []
    for glob_pattern, loader_cls in loaders.items():
        loader = DirectoryLoader(
            directory_path,
            glob=glob_pattern,
            loader_cls=loader_cls,
        )
        all_docs.extend(loader.load())
    
    return all_docs

# 2. Dökümanları chunk'la
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Her parça max 1000 karakter
    chunk_overlap=200,    # Parçalar arası 200 karakter örtüşme
    separators=["\n\n", "\n", ".", " "]
)

documents = load_knowledge_base("./knowledge_base/")
chunks = text_splitter.split_documents(documents)
print(f"Toplam {len(chunks)} chunk oluşturuldu")

# 3. Embedding modeli
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    # Türkçe için alternatif: "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr"
)

# 4. Vektör veritabanı oluştur
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name="sales_marketing_kb"
)

# 5. Retriever oluştur
retriever = vectorstore.as_retriever(
    search_type="mmr",          # Maximum Marginal Relevance — çeşitlilik sağlar
    search_kwargs={"k": 5}      # En ilgili 5 parçayı getir
)

# 6. Sorgu örneği
query = "E-ticaret sektöründe ortalama Facebook Ads CTR nedir?"
relevant_docs = retriever.get_relevant_documents(query)
for doc in relevant_docs:
    print(f"Kaynak: {doc.metadata['source']}")
    print(f"İçerik: {doc.page_content[:200]}...")
    print("---")
```

### Vektör DB alternatifleri

| Veritabanı | Avantaj | Kullanım |
|------------|---------|----------|
| ChromaDB | Kolay kurulum, yerel çalışır | Küçük-orta ölçek |
| Pinecone | Yönetilen servis, ölçeklenebilir | Üretim ortamı |
| Weaviate | Hybrid search (metin + vektör) | Gelişmiş arama |
| Qdrant | Hızlı, Rust tabanlı | Yüksek performans |
| pgvector | PostgreSQL eklentisi | Mevcut DB varsa |

---

## KATMAN 3: Tool / Agent Katmanı (EL & GÖZ)

### Ne işe yarar?

Model "düşünebilir" ama "yapamaz." Tool katmanı modele şu yetenekleri verir:
- Excel/CSV dosyası okuma ve yazma
- Python kodu çalıştırma (istatistik, grafik)
- Meta Ads API'den veri çekme
- Google Ads API'den veri çekme
- Web'den güncel bilgi arama
- Rapor ve grafik oluşturma

### Tool tanımlamaları

```python
# LangChain Agent ile Tool Tanımlama

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool, StructuredTool
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
import matplotlib.pyplot as plt

# Tool 1: Excel/CSV Okuyucu
def read_spreadsheet(file_path: str) -> str:
    """Excel veya CSV dosyasını okuyup özet istatistiklerini döndürür."""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    summary = f"""
    Dosya: {file_path}
    Satır sayısı: {len(df)}
    Sütunlar: {', '.join(df.columns.tolist())}
    
    İlk 5 satır:
    {df.head().to_string()}
    
    Temel istatistikler:
    {df.describe().to_string()}
    """
    return summary

spreadsheet_tool = Tool(
    name="read_spreadsheet",
    func=read_spreadsheet,
    description="Excel (.xlsx) veya CSV dosyasını okur ve özet istatistiklerini döndürür."
)

# Tool 2: Kampanya Analiz Aracı
def analyze_campaign(data_json: str) -> str:
    """Kampanya verilerini analiz eder, KPI hesaplar ve benchmark karşılaştırması yapar."""
    import json
    data = json.loads(data_json)
    df = pd.DataFrame(data)
    
    # KPI hesaplamaları
    if 'impressions' in df.columns and 'clicks' in df.columns:
        df['ctr'] = (df['clicks'] / df['impressions'] * 100).round(2)
    if 'spend' in df.columns and 'clicks' in df.columns:
        df['cpc'] = (df['spend'] / df['clicks']).round(2)
    if 'spend' in df.columns and 'conversions' in df.columns:
        df['cpa'] = (df['spend'] / df['conversions']).round(2)
    if 'revenue' in df.columns and 'spend' in df.columns:
        df['roas'] = (df['revenue'] / df['spend']).round(2)
    
    return df.to_json(orient='records')

campaign_tool = Tool(
    name="analyze_campaign",
    func=analyze_campaign,
    description="Kampanya verilerini JSON formatında alır, KPI hesaplar (CTR, CPC, CPA, ROAS)."
)

# Tool 3: Grafik Oluşturucu
def create_chart(chart_config: str) -> str:
    """Verilen konfigürasyona göre grafik oluşturur ve kaydeder."""
    import json
    config = json.loads(chart_config)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    chart_type = config.get('type', 'bar')
    if chart_type == 'bar':
        ax.bar(config['labels'], config['values'], color=config.get('color', '#4CAF50'))
    elif chart_type == 'line':
        ax.plot(config['labels'], config['values'], marker='o', color=config.get('color', '#2196F3'))
    elif chart_type == 'pie':
        ax.pie(config['values'], labels=config['labels'], autopct='%1.1f%%')
    
    ax.set_title(config.get('title', 'Grafik'))
    ax.set_xlabel(config.get('xlabel', ''))
    ax.set_ylabel(config.get('ylabel', ''))
    
    output_path = f"./output/{config.get('filename', 'chart')}.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return f"Grafik kaydedildi: {output_path}"

chart_tool = Tool(
    name="create_chart",
    func=create_chart,
    description="Grafik oluşturur. JSON config alır: type (bar/line/pie), labels, values, title."
)

# Tool 4: Meta Ads API Bağlantısı
def fetch_meta_ads(params: str) -> str:
    """Meta Marketing API'den kampanya verilerini çeker."""
    import json
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    
    config = json.loads(params)
    
    FacebookAdsApi.init(
        app_id=config['app_id'],
        app_secret=config['app_secret'],
        access_token=config['access_token'],
    )
    
    account = AdAccount(f"act_{config['account_id']}")
    
    insights = account.get_insights(
        fields=[
            'campaign_name', 'impressions', 'clicks', 'spend',
            'actions', 'ctr', 'cpc', 'cpp', 'cpm',
        ],
        params={
            'date_preset': config.get('date_preset', 'last_30d'),
            'level': config.get('level', 'campaign'),
        }
    )
    
    return json.dumps([dict(insight) for insight in insights], indent=2)

meta_ads_tool = Tool(
    name="fetch_meta_ads",
    func=fetch_meta_ads,
    description="Meta Ads API'den kampanya verilerini çeker. Account ID ve tarih aralığı gerektirir."
)

# Tool 5: Python Kod Çalıştırıcı (dikkatli kullan)
def run_python_code(code: str) -> str:
    """Python kodu çalıştırır ve sonucunu döndürür."""
    import io, contextlib
    
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {"pd": pd, "plt": plt, "np": __import__('numpy')})
        return output.getvalue() or "Kod başarıyla çalıştı."
    except Exception as e:
        return f"Hata: {str(e)}"

python_tool = Tool(
    name="run_python",
    func=run_python_code,
    description="Python kodu çalıştırır. Pandas, matplotlib, numpy kullanılabilir."
)
```

### Agent'ı birleştirme

```python
# Tüm katmanları birleştiren Agent

from langchain_community.llms import VLLM  # veya HuggingFacePipeline
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

# 1. Fine-tuned modeli yükle
llm = VLLM(
    model="./sales-marketing-llm-final",
    trust_remote_code=True,
    max_new_tokens=4096,
    temperature=0.3,
)

# 2. RAG retriever'ı tool olarak ekle
def search_knowledge_base(query: str) -> str:
    """Bilgi bankasından ilgili dökümanları arar."""
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return context

kb_tool = Tool(
    name="search_knowledge_base",
    func=search_knowledge_base,
    description="Satış psikolojisi, reklam stratejileri, sektör benchmarkları hakkında bilgi arar."
)

# 3. Tüm tool'ları listele
tools = [
    spreadsheet_tool,
    campaign_tool,
    chart_tool,
    meta_ads_tool,
    python_tool,
    kb_tool,
]

# 4. System prompt
system_prompt = """Sen bir satış psikolojisi ve dijital reklam stratejisi uzmanısın. 
Türkiye pazarını iyi bilirsin. Görevin:

1. Kullanıcının reklam/satış verilerini analiz etmek
2. Performans sorunlarını tespit etmek
3. Satış psikolojisi ve ikna tekniklerine dayalı öneriler sunmak
4. Somut, uygulanabilir aksiyon planları oluşturmak

Analiz yaparken:
- Önce verileri oku (read_spreadsheet veya fetch_meta_ads kullan)
- Sektör benchmarklarını kontrol et (search_knowledge_base kullan)
- KPI hesapla (analyze_campaign kullan)
- Görselleştirme yap (create_chart kullan)
- Stratejik önerilerini sun

Her zaman somut rakamlar ve örnekler ver. Jenerik tavsiyelerden kaçın."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 5. Memory (konuşma geçmişi)
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    return_messages=True,
    k=10  # Son 10 mesajı hatırla
)

# 6. Agent oluştur
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,          # Debug için tool çağrılarını göster
    max_iterations=10,     # Maksimum tool çağrısı sayısı
    handle_parsing_errors=True,
)

# 7. Kullan!
response = agent_executor.invoke({
    "input": "Şu Excel dosyasını analiz et: kampanya_raporu.xlsx"
})
print(response["output"])
```

---

## BONUS: Web Arayüzü

Tüm sistemi bir web arayüzüne sarmak için:

### Seçenek 1: Gradio (en kolay)

```python
import gradio as gr

def chat(message, history, file):
    # Dosya yüklendiyse önce kaydet
    if file:
        file_path = f"./uploads/{file.name}"
        # Dosyayı kaydet ve agent'a bildir
        response = agent_executor.invoke({
            "input": f"Bu dosyayı analiz et: {file_path}\n\nKullanıcı mesajı: {message}"
        })
    else:
        response = agent_executor.invoke({"input": message})
    
    return response["output"]

demo = gr.ChatInterface(
    fn=chat,
    title="Satış & Reklam AI Asistanı",
    description="Reklam verilerinizi yükleyin, stratejik analiz alın.",
    additional_inputs=[
        gr.File(label="Kampanya Verisi (Excel/CSV)")
    ],
    examples=[
        ["Meta Ads kampanyamın CTR'ı %0.5, nasıl artırabilirim?"],
        ["Google Ads Quality Score'um düşük, ne yapmalıyım?"],
        ["E-ticaret için en etkili ikna teknikleri neler?"],
    ]
)

demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
```

### Seçenek 2: Streamlit (daha özelleştirilebilir)

```python
import streamlit as st

st.title("🎯 Satış & Reklam AI Asistanı")

uploaded_file = st.file_uploader("Kampanya verisi yükle", type=['xlsx', 'csv'])

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Sorunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        response = agent_executor.invoke({"input": prompt})
        st.markdown(response["output"])
    
    st.session_state.messages.append({"role": "assistant", "content": response["output"]})
```

---

## Uygulama Yol Haritası

### Faz 1: Temel Kurulum (1-2 hafta)
- [ ] Base model seç (Llama 3.1 8B önerilir)
- [ ] Veri setlerini indir ve temizle
- [ ] İlk 500 instruction örneği oluştur
- [ ] İlk fine-tuning denemesi yap
- [ ] Sonuçları değerlendir

### Faz 2: RAG Entegrasyonu (1 hafta)
- [ ] Bilgi bankası dökümanlarını topla
- [ ] ChromaDB kur ve dökümanları indexle
- [ ] Retriever'ı test et
- [ ] Fine-tuned model + RAG'ı birleştir

### Faz 3: Tool Entegrasyonu (1-2 hafta)
- [ ] Excel/CSV okuyucu tool'u yap
- [ ] Kampanya analiz tool'u yap
- [ ] Grafik oluşturucu tool'u yap
- [ ] Agent'ı oluştur ve test et

### Faz 4: API Bağlantıları (1 hafta)
- [ ] Meta Marketing API entegrasyonu
- [ ] Google Ads API entegrasyonu
- [ ] Otomatik veri çekme pipeline'ı

### Faz 5: Arayüz ve Deploy (1 hafta)
- [ ] Gradio veya Streamlit arayüzü
- [ ] Docker containerize
- [ ] Cloud deploy (AWS/GCP/Hetzner)
- [ ] Kullanıcı testi ve iterasyon

### Faz 6: Sürekli İyileştirme (devam eden)
- [ ] Kullanıcı feedbacklerini topla
- [ ] Veri setini genişlet (hedef 5000+ örnek)
- [ ] Modeli yeniden fine-tune et
- [ ] RAG bilgi bankasını güncelle

---

## Maliyet Tahmini

| Kalem | Tek Seferlik | Aylık |
|-------|-------------|-------|
| Fine-tuning (RunPod/Colab) | ~50-100$ | — |
| GPU sunucu (inference) | — | ~100-300$/ay |
| Vektör DB (Pinecone free tier) | — | 0$ (başlangıç) |
| Meta API | — | 0$ (kendi hesabın) |
| Google Ads API | — | 0$ (kendi hesabın) |
| Domain + Hosting | — | ~20$/ay |
| **TOPLAM** | **~100-150$** | **~120-320$/ay** |

**Düşük bütçe alternatifi:** Kendi fine-tuned modelini kullanmak yerine, OpenAI GPT-4o-mini fine-tuning + RAG ile başlayabilirsin. Maliyet çok daha düşük olur (~25$/ay) ama model üzerinde tam kontrol olmaz.

---

## Önemli Uyarılar

1. **Fine-tuning kalitesi = Veri kalitesi.** Çöp girerse çöp çıkar. 100 mükemmel örnek, 10,000 kötü örnekten iyidir.

2. **Türkçe veri kıtlığı gerçek bir sorun.** İngilizce veri setleri çok daha zengin. Hybrid bir yaklaşım (İngilizce eğitim + Türkçe instruction örnekleri) daha iyi sonuç verebilir.

3. **RAG her zaman fine-tuning'den önce dene.** Bazen sadece iyi bir RAG sistemi + güçlü base model (GPT-4, Claude) fine-tuning'e gerek kalmadan yeterli olabilir.

4. **Hallucination riski:** Model uydurma rakamlar verebilir. RAG ile desteklenmemiş istatistikleri "kaynak belirtilmemiş" olarak işaretle.

5. **Yasal sorumluluk:** AI'ın reklam stratejisi önerilerini direkt uygulamadan önce mutlaka insan denetiminden geçir. Özellikle bütçe kararlarında.
