

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv # Importar dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar componentes do OTTO
# O OTTOAgent será o orquestrador central
from core.llm_manager import LLMManager
from core.vector_store import VectorStoreManager
from core.memory_manager import FirebaseMemoryManager as MemoryManager # Renomeado para compatibilidade
from core.agent import OTTOAgent
from funcoes.redacao_tool import RedacaoTool # Importar a ferramenta de redação

# Modelos de entrada
class ChatIn(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    conversation_date: Optional[str] = None

class RedacaoIn(BaseModel):
    user_id: str
    essay_text: str
    essay_topic: Optional[str] = None

# Inicializar componentes fora do lifespan para evitar problemas de aclose() com o cliente Gemini
llm_manager = LLMManager()
vector_store_manager = VectorStoreManager()
memory_manager = MemoryManager()
agent = OTTOAgent(llm_manager, vector_store_manager, memory_manager)
redacao_tool = RedacaoTool(llm_manager, vector_store_manager)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OTTO - Assistente de IA para Professores",
    description="API Backend para o assistente educacional OTTO.",
    version="1.0.0"
)

# Configuração do CORS
origins = [
    "http://localhost:5173",  # Porta padrão do Vite/React
    "http://127.0.0.1:5173",
    # Adicione outros domínios de frontend se necessário
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar componentes ao estado do app para acesso nos endpoints
app.state.agent = agent
app.state.llm_manager = llm_manager
app.state.vector_store_manager = vector_store_manager
app.state.memory_manager = memory_manager
app.state.redacao_tool = redacao_tool

logger.info("Componentes do OTTO inicializados com sucesso (fora do lifespan).")

@app.get("/")
async def root():
    return {"message": "OTTO API está online!"}

@app.post("/chat", response_model=Dict[str, Any])
async def chat_endpoint(payload: ChatIn, request: Request):
    """Endpoint principal para o chat conversacional."""
    agent = request.app.state.agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Serviço OTTO indisponível. Falha na inicialização.")
    
    # O OTTOAgent agora orquestra todo o fluxo (histórico, RAG, LLM)
    resposta = agent.process_query(
        user_id=payload.user_id,
        message=payload.message,
        conversation_id=payload.conversation_id,
        conversation_date=payload.conversation_date
    )
    
    if not resposta["success"]:
        raise HTTPException(status_code=500, detail=resposta["error"])
        
    return resposta

@app.post("/redacao", response_model=Dict[str, Any])
async def redacao_endpoint(payload: RedacaoIn, request: Request):
    """Endpoint para correção de redação."""
    redacao_tool = request.app.state.redacao_tool
    
    if redacao_tool is None:
        raise HTTPException(status_code=503, detail="Serviço de Redação indisponível. Falha na inicialização.")
        
    # A ferramenta de redação é chamada diretamente
    resultado = redacao_tool.corrigir_redacao(
        user_id=payload.user_id,
        essay_text=payload.essay_text,
        essay_topic=payload.essay_topic
    )
    
    if not resultado["success"]:
        raise HTTPException(status_code=500, detail=resultado["error"])
        
    return resultado