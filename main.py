from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from core.llm_manager import LLMManager
from core.vector_store import VectorStoreManager
from core.memory_manager import MemoryManager
from core.agent import OTTOAgent
from typing import Optional
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando componentes...")

    llm_manager = LLMManager()
    vector_store_manager = VectorStoreManager()
    memory_manager = MemoryManager()
    agent = OTTOAgent(llm_manager, vector_store_manager, memory_manager)

    # 🔹 salvar todos no estado do app
    app.state.agent = agent
    app.state.llm_manager = llm_manager
    app.state.vector_store_manager = vector_store_manager
    app.state.memory_manager = memory_manager

    yield  # depois disso é o shutdown
    print("Encerrando aplicação...")

app = FastAPI(lifespan=lifespan)

class ChatIn(BaseModel):
    pergunta: str

@app.post("/chat")
async def chat_endpoint(payload: ChatIn, request: Request):
    agent = request.app.state.agent
    if agent is None:
        raise HTTPException(500, "Agent não inicializado")
    resposta = agent.process_query(payload.pergunta, user_id="")
    return {"resposta": resposta}

class RedacaoIn(BaseModel):
    texto: str
    tema: Optional[str] = None

@app.post("/redacao")
async def redacao_endpoint(payload: RedacaoIn, request: Request):
    llm = request.app.state.llm_manager
    vs = request.app.state.vector_store_manager

    # carregar / criar store
    vs_dir = "./data/redacao"
    redacao_store = vs.create_or_load("redacao_knowledge", vs_dir)

    prompt = f"""
    Você é um corretor de redações do ENEM. 
    Corrija o texto abaixo e dê uma nota de 0 a 1000.
    Tema: {payload.tema if payload.tema else "Tema livre"}
    
    TEXTO DO ALUNO:
    {payload.texto}
    """

    resultado = llm.generate(prompt, temperature=0.2)
    return {"resposta": resultado}
