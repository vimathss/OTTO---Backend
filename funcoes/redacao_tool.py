"""
RedacaoTool - Ferramenta de correção de redação para o OTTO

Este módulo implementa a ferramenta de correção de redação que acessa
documentos específicos sobre correção de redação e utiliza o LLMManager.
"""

import os
import logging
from typing import Dict, Any, Optional
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class RedacaoTool:
    """
    Ferramenta de correção de redação que utiliza RAG e LLM.
    """
    
    def __init__(self, llm_manager, vector_store_manager):
        self.llm_manager = llm_manager
        self.vector_store_manager = vector_store_manager
        self.redacao_store_name = "redacao_knowledge"
        self.redacao_docs_dir = "./data/redacao"
        
        # Garantir que o diretório de dados exista
        os.makedirs(self.redacao_docs_dir, exist_ok=True)
        
        # Tentar carregar ou criar o vector store de redação
        try:
            self.redacao_store = self.vector_store_manager.get_store(self.redacao_store_name)
            if not self.redacao_store:
                # Se não existe, tenta criar (assumindo que o script de ingestão será executado separadamente)
                # Se o diretório estiver vazio, o create_or_load falhará, o que é esperado.
                logger.warning(f"Vector store '{self.redacao_store_name}' não encontrado. Tentando carregar/criar...")
                self.redacao_store = self.vector_store_manager.create_or_load(self.redacao_store_name, self.redacao_docs_dir)
            
            if not self.redacao_store:
                logger.error(f"Falha ao inicializar o vector store de redação. A correção de redação usará apenas o conhecimento do LLM.")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar RedacaoTool: {e}")
            self.redacao_store = None
            
        logger.info("RedacaoTool inicializado.")

    def corrigir_redacao(
        self,
        user_id: str,
        essay_text: str,
        essay_topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Corrige uma redação usando o LLM e a base de conhecimento de redação.
        """
        try:
            # 1. Recuperar conhecimento relevante (RAG)
            conhecimento_redacao = self._get_knowledge_context()
            
            # 2. Construir prompt para correção
            prompt = self._build_correction_prompt(essay_text, essay_topic, conhecimento_redacao)
            
            # 3. Gerar correção (usando generate_response do LLMManager)
            # Como é uma tarefa não-conversacional, não passamos histórico (context=None)
            llm_response = self.llm_manager.generate_response(
                prompt=prompt,
                context=None,
                system_prompt="Você é um especialista rigoroso em correção de redações do ENEM. Analise a redação e forneça uma análise detalhada e construtiva, seguindo rigorosamente os critérios de avaliação fornecidos no prompt.",
                config={"temperature": 0.2}
            )
            
            if llm_response["success"]:
                return {
                    "success": True,
                    "content": llm_response["content"],
                    "user_id": user_id,
                    "knowledge_used": bool(conhecimento_redacao.strip()),
                    "sources": ["Base de Conhecimento de Redação" if conhecimento_redacao.strip() else "Conhecimento Geral do LLM"]
                }
            else:
                return {
                    "success": False,
                    "error": llm_response.get("error", "Erro desconhecido na geração do LLM."),
                    "user_id": user_id
                }
                
        except Exception as e:
            logger.error(f"Erro ao corrigir redação: {e}")
            return {
                "success": False,
                "error": f"Erro interno ao processar a correção: {str(e)}",
                "user_id": user_id
            }

    def _get_knowledge_context(self) -> str:
        """
        Busca conhecimento relevante na base de redação.
        """
        if not self.redacao_store:
            return self._default_knowledge()
            
        try:
            # Busca por critérios e exemplos de correção
            results_with_scores = self.redacao_store.similarity_search_with_score(
                query="critérios correção redação ENEM exemplos", 
                k=5
            )
            
            relevant_results = [
                doc.page_content for doc, score in results_with_scores
                if score < 0.7 # Threshold de relevância
            ]
            
            if relevant_results:
                return "\n\n".join(relevant_results)
            else:
                return self._default_knowledge()
                
        except Exception as e:
            logger.error(f"Erro na busca RAG para correção de redação: {e}")
            return self._default_knowledge()

    def _default_knowledge(self) -> str:
        """
        Retorna o conhecimento padrão se o RAG falhar.
        """
        return """
        Critérios de Avaliação da Redação do ENEM:

        Competência 1: Demonstrar domínio da norma padrão da língua escrita.
        Competência 2: Compreender a proposta de redação e aplicar conceitos das várias áreas de conhecimento para desenvolver o tema, dentro dos limites estruturais do texto dissertativo-argumentativo.
        Competência 3: Selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista.
        Competência 4: Demonstrar conhecimento dos mecanismos linguísticos necessários para a construção da argumentação.
        Competência 5: Elaborar proposta de intervenção para o problema abordado, respeitando os direitos humanos.

        Cada competência vale de 0 a 200 pontos, totalizando 1000 pontos.
        """

    def _build_correction_prompt(self, essay_text: str, essay_topic: Optional[str], knowledge: str) -> str:
        """
        Constrói o prompt final para o LLM.
        """
        return f"""
        TEXTO DA REDAÇÃO:
        {essay_text}

        {f"TEMA DA REDAÇÃO: {essay_topic}" if essay_topic else ""}

        CRITÉRIOS DE AVALIAÇÃO E EXEMPLOS DE REDAÇÕES NOTA MÁXIMAS COM COMENTÁRIOS DE CORRETORES:
        {knowledge}

        Forneça uma análise detalhada seguindo este formato:
        1. Competência 1 (Domínio da norma culta): [nota 0-200] - [justificativa detalhada]
        2. Competência 2 (Compreensão do tema): [nota 0-200] - [justificativa detalhada]
        3. Competência 3 (Organização de argumentos): [nota 0-200] - [justificativa detalhada]
        4. Competência 4 (Construção da argumentação): [nota 0-200] - [justificativa detalhada]
        5. Competência 5 (Proposta de intervenção): [nota 0-200] - [justificativa detalhada]

        NOTA FINAL: [soma das notas]

        FEEDBACK GERAL:
        [Resumo dos pontos fortes]
        [Resumo dos pontos a melhorar]
        [Sugestões específicas para aprimoramento]

        Seja educativo, construtivo e específico no feedback, apontando exemplos concretos do texto.

        Caso o texto não esteja em formato dissertativo-argumentativo ou não seja uma redação, informe que a redação não atende aos requisitos e que o usuario deve tentar novamente com um texto adequado.
        """
