"""
Agente Principal - Coordenador central do OTTO

Este módulo implementa o agente principal que coordena todos os componentes do OTTO,
processando consultas e direcionando para as ferramentas apropriadas.
"""

from typing import Dict, Any, Optional
import logging

class OTTOAgent:
    """Agente principal que coordena ferramentas e responde consultas."""
    
    def __init__(self, llm_manager, vector_store_manager, memory_manager):
        self.llm_manager = llm_manager
        self.vector_store_manager = vector_store_manager
        self.memory_manager = memory_manager
        
        # Verificar se temos um vector store principal
        self.general_vector_store = self.vector_store_manager.get_main_store()
        if not self.general_vector_store:
            logging.warning("Vector store principal não encontrado. Algumas funcionalidades podem não estar disponíveis.")
    
    def process_query(self, query: str, user_id: str = "default_user") -> str:
        """Processa uma consulta do usuário."""
        # Carregar contexto da conversa
        conversation_context = self.memory_manager.get_context(user_id)
        
        # Comandos especiais
        if query.lower() == "limpar histórico":
            self.memory_manager.clear_history(user_id)
            return "Histórico de conversa limpo."
        
        response = self._handle_general_query(query, conversation_context)
        
        # Atualizar memória
        self.memory_manager.add_interaction(user_id, query, response)
        
        return response

    
    def _handle_general_query(self, query: str, context: Dict[str, Any]) -> str:
        """Processa consultas gerais usando RAG."""
        # Verificar se temos um vector store
        if not self.general_vector_store:
            # Fallback para LLM sem contexto de documentos
            return self._generate_response_without_context(query, context)
        
        # Recuperar documentos relevantes
        try:
            docs = self.general_vector_store.similarity_search(query, k=5)
            doc_content = "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logging.error(f"Erro ao recuperar documentos: {e}")
            doc_content = "Não foi possível recuperar informações relevantes dos documentos."
        
        # Construir prompt com contexto da conversa
        history = context.get("conversation_history", "")
        
        prompt = f"""
        Você é o assistente educacional OTTO, capaz de responder perguntas sobre horários escolares, BNCC, ABNT e elaboração de planos de aula.
        
        Histórico da conversa:
        {history}
        
        Contexto relevante dos documentos:
        {doc_content}
        
        Pergunta atual do usuário:
        {query}
        
        Responda de forma educativa e clara, considerando o histórico da conversa quando relevante.
        """
        
        # Gerar resposta
        response = self.llm_manager.generate(prompt)
        
        return response
    
    def _generate_response_without_context(self, query: str, context: Dict[str, Any]) -> str:
        """Gera resposta sem contexto de documentos."""
        history = context.get("conversation_history", "")
        
        prompt = f"""
        Você é um assistente educacional, capaz de responder perguntas sobre educação, BNCC, ABNT e elaboração de planos de aula.
        
        Histórico da conversa:
        {history}
        
        Pergunta atual do usuário:
        {query}
        
        Responda de forma educativa e clara, considerando o histórico da conversa quando relevante.
        """
        
        return self.llm_manager.generate(prompt)
