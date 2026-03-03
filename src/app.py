import os
import json
import logging
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr
from langchain_community.llms import VLLM
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import Tool
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config & Paths
MODEL_PATH = os.environ.get("MODEL_PATH", "./output/satis-reklam-ai/checkpoint-final")
KB_DIR = "./knowledge_base"
CHROMA_DIR = "./chroma_db"
UPLOADS_DIR = "./uploads"
OUTPUT_DIR = "./output"

# Klasörleri oluştur (eğer yoksa)
os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. RAG SİSTEMİ (Hazırlık)
# ---------------------------------------------------------------------------
def init_rag():
    logger.info("RAG Sistemi başlatılıyor...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Bilgi bankasında belge varsa Chroma oluşturulur / güncellenir
    files = os.listdir(KB_DIR) if os.path.exists(KB_DIR) else []
    
    if files:
        logger.info(f"{KB_DIR} içinde {len(files)} dosya bulundu. Vektör DB hazırlanıyor...")
        loaders = {
            "**/*.txt": TextLoader,
            "**/*.pdf": PyPDFLoader,
            "**/*.csv": CSVLoader,
        }
        all_docs = []
        for glob_pattern, loader_cls in loaders.items():
            loader = DirectoryLoader(KB_DIR, glob=glob_pattern, loader_cls=loader_cls)
            all_docs.extend(loader.load())
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(all_docs)
        
        vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR, collection_name="sales_marketing_kb")
    else:
        logger.warning(f"Bilgi bankası boş: {KB_DIR}. Sadece mevcut veya boş Chroma DB yüklenecek.")
        vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings, collection_name="sales_marketing_kb")
        
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    return retriever

try:
    retriever = init_rag()
except Exception as e:
    logger.error(f"RAG init hatası: {e}")
    retriever = None

# Soru Cevaplama Aracı (RAG)
def search_knowledge_base(query: str) -> str:
    if not retriever:
        return "Bilgi bankası şu an aktif değil veya boş."
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return context

kb_tool = Tool(
    name="search_knowledge_base",
    func=search_knowledge_base,
    description="Satış psikolojisi, reklam stratejileri, sektör benchmarkları hakkında bilgi arar."
)

# ---------------------------------------------------------------------------
# 2. ARAÇLAR (Tools)
# ---------------------------------------------------------------------------
def read_spreadsheet(file_path: str) -> str:
    """Excel veya CSV dosyasını okuyup özet istatistiklerini döndürür."""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        summary = f"Dosya: {file_path}\nSatır: {len(df)} Sütunlar: {', '.join(df.columns)}\n\n"
        summary += f"Önizleme:\n{df.head().to_string()}\n\n"
        summary += f"İstatistikler:\n{df.describe().to_string()}"
        return summary
    except Exception as e:
        return f"Dosya okunurken hata oluştu: {str(e)}"

spreadsheet_tool = Tool(
    name="read_spreadsheet",
    func=read_spreadsheet,
    description="Excel (.xlsx) veya CSV dosyasını okur ve özet istatistiklerini döndürür."
)

def analyze_campaign(data_json: str) -> str:
    """Kampanya verilerini analiz eder, KPI hesaplar."""
    try:
        data = json.loads(data_json)
        df = pd.DataFrame(data)
        
        if 'impressions' in df.columns and 'clicks' in df.columns:
            df['ctr'] = (df['clicks'] / df['impressions'] * 100).round(2)
        if 'spend' in df.columns and 'clicks' in df.columns:
            df['cpc'] = (df['spend'] / df['clicks']).round(2)
        if 'spend' in df.columns and 'conversions' in df.columns:
            df['cpa'] = (df['spend'] / df['conversions']).round(2)
        if 'revenue' in df.columns and 'spend' in df.columns:
            df['roas'] = (df['revenue'] / df['spend']).round(2)
            
        return df.to_json(orient='records')
    except Exception as e:
        return f"Analiz hatası: {str(e)}"

campaign_tool = Tool(
    name="analyze_campaign",
    func=analyze_campaign,
    description="Kampanya verilerini JSON formatında alır, KPI hesaplar (CTR, CPC, CPA, ROAS)."
)

def run_python_code(code: str) -> str:
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

tools = [spreadsheet_tool, campaign_tool, python_tool, kb_tool]

# ---------------------------------------------------------------------------
# 3. LLM ve AGENT
# ---------------------------------------------------------------------------
def init_agent():
    try:
        logger.info(f"Model yükleniyor: {MODEL_PATH}")
        # Not: Qwen3-VL 4-bit config'i tam oturtulduktan sonra Inference için Llama-cpp veya VLLM güncellenebilir
        # Local model bulunmazsa placeholder fallback 
        llm = VLLM(model=MODEL_PATH, trust_remote_code=True, max_new_tokens=4096, temperature=0.3)
    except Exception as e:
        logger.warning(f"VLLM ile model yüklenemedi, ChatOllama veya base fallback devrede: {e}")
        llm = None
        
    system_prompt = """Sen bir satış psikolojisi ve dijital reklam stratejisi uzmanısın. Türkiye pazarını iyi bilirsin.
1. Kullanıcının reklam/satış verilerini analiz et
2. Performans sorunlarını tespit et
3. Satış psikolojisi ve ikna tekniklerine dayalı öneriler sun
4. Somut, uygulanabilir aksiyon planları oluştur

Araçları kullanarak (dosya okuma, KPI hesaplama) sayısal verileri dikkate al.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=10)
    
    if llm:
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True, max_iterations=10, handle_parsing_errors=True)
        return agent_executor
    return None

agent_executor = init_agent()

# ---------------------------------------------------------------------------
# 4. GRADIO UI
# ---------------------------------------------------------------------------
def chat_fn(message, history, file):
    if not agent_executor:
        return "Sistem şu an hazır değil: Model henüz fine-tune edilmedi veya bulunamadı."
        
    try:
        if file:
            import shutil
            file_name = os.path.basename(file.name)
            save_path = os.path.join(UPLOADS_DIR, file_name)
            shutil.copy(file.name, save_path)
            
            prompt = f"Şu dosyayı analiz et: {save_path}\n\nKullanıcı sorusu: {message}"
            response = agent_executor.invoke({"input": prompt})
        else:
            response = agent_executor.invoke({"input": message})
            
        return response.get("output", str(response))
    except Exception as e:
        return f"Sistem Hatası: {str(e)}"

# Gradio arayüzü
demo = gr.ChatInterface(
    fn=chat_fn,
    title="🎯 Satış & Reklam AI Asistanı",
    description="Qwen3-VL QLoRA tabanlı, RAG destekli AI ajanınız. Reklam verilerinizi (Excel/CSV) yükleyin, stratejik analiz alın.",
    additional_inputs=[gr.File(label="Örnek Kampanya Verisi (Excel/CSV)")],
    examples=[
        ["Meta Ads kampanyamın tıklama oranı (CTR) %0.5, nasıl artırabilirim?"],
        ["Google Ads Cost-per-Acquisition (CPA) rakamlarımı düşürmek için hangi psikolojik tetikleyicileri kullanmalıyım?"],
    ]
)

if __name__ == "__main__":
    logger.info("Arayüz 0.0.0.0:7860 üzerinde başlatılıyor...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
