"""
LLM Manager - Gerenciador de modelos de linguagem para o OTTO

Este módulo gerencia diferentes modelos de linguagem, priorizando API Gemini
com fallback para execução local através do Ollama quando necessário.

Api Reserva: AIzaSyAtI3pItCogbK7jEZhSF2U11boiCJYxqUI
"""

import os
import psutil
import logging
from typing import Dict, Any, Optional

class LLMManager:
    """Gerencia diferentes modelos de linguagem."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.available_ram = self._get_available_ram()
        # Usar a API key fornecida
        self.api_key = "AIzaSyBJJYkukxH78965IdPVvKKttcXpYYzpRK8"
        self.llm = None
        print(f"RAM disponível: {self.available_ram} MB")
        self.initialize()
        
    def _get_available_ram(self) -> float:
        """Detecta RAM disponível em MB."""
        return psutil.virtual_memory().available / (1024 * 1024)
    
    def initialize(self) -> None:
        """Inicializa o melhor LLM disponível com base nos recursos."""
        print("Tentando inicializar LLM...")
        
        # Tentar inicializar API Gemini primeiro
        try:
            print("Tentando inicializar API Gemini...")
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.2
            )
            logging.info("Inicializado modelo via API: gemini-2.5-flash")
            print("API Gemini inicializada com sucesso!")
            return
        except Exception as e:
            logging.warning(f"Erro ao inicializar API Gemini: {e}")
            print(f"Erro ao inicializar API Gemini: {e}")
        
        # Fallback para modelos locais
        models = [
            {"name": "gemma:2b-instruct-q4_0", "min_ram": 1024, "provider": "ollama"},
            {"name": "tinyllama", "min_ram": 2048, "provider": "ollama"},
            #{"name": "llama3.2", "min_ram": 1096, "provider": "ollama"},

        ]
        
        # Tentar inicializar modelos locais
        for model in models:
            print(f"Tentando inicializar modelo: {model['name']} (RAM mínima: {model['min_ram']} MB)")
            if self.available_ram >= model["min_ram"]:
                try:
                    if model["provider"] == "ollama":
                        from langchain_community.llms import Ollama
                        self.llm = Ollama(
                            model=model["name"],
                            num_gpu=0,  # Forçar CPU apenas
                            num_thread=min(4, os.cpu_count() or 2)  # Limitar threads
                        )
                        logging.info(f"Inicializado modelo local: {model['name']}")
                        print(f"Modelo local {model['name']} inicializado com sucesso!")
                        return
                except Exception as e:
                    logging.warning(f"Erro ao inicializar modelo {model['name']}: {e}")
                    print(f"Erro ao inicializar modelo {model['name']}: {e}")
        
        # Mensagem de erro se nenhum modelo puder ser inicializado
        error_msg = "Não foi possível inicializar nenhum LLM. Verifique a instalação do Ollama ou a API key."
        logging.error(error_msg)
        print(error_msg)
        raise RuntimeError(error_msg)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Gera resposta com fallback automático."""
        if not self.llm:
            raise RuntimeError("LLM não inicializado")
            
        try:
            print("Gerando resposta...")
            response = self.llm.invoke(prompt, **kwargs)
            # Processar resposta conforme o tipo retornado
            if hasattr(response, 'content'):
                return response.content
            return str(response)
        except Exception as e:
            logging.error(f"Erro ao gerar resposta: {e}")
            print(f"Erro ao gerar resposta: {e}")
            
            # Tentar fallback para API se estávamos usando modelo local
            if not str(type(self.llm)).endswith("ChatGoogleGenerativeAI'>"):
                try:
                    print("Tentando fallback para API Gemini...")
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    api_llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash",
                        google_api_key=self.api_key
                    )
                    response = api_llm.invoke(prompt, **kwargs)
                    if hasattr(response, 'content'):
                        return response.content
                    return str(response)
                except Exception as e2:
                    logging.error(f"Erro no fallback para API: {e2}")
                    print(f"Erro no fallback para API: {e2}")
            
            # Mensagem de erro amigável se tudo falhar
            return "Desculpe, estou enfrentando dificuldades técnicas para processar sua solicitação. Por favor, tente uma pergunta mais simples ou tente novamente mais tarde."
