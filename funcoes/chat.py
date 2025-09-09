"""
Chat interativo com o OTTO - Interface simples para testar o assistente.
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Ajustar o caminho para importar módulos corretamente

import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("otto_chat.log"),
        logging.StreamHandler()
    ]
)

# Importar componentes do OTTO
from core.llm_manager import LLMManager
from core.memory_manager import MemoryManager
from core.vector_store import VectorStoreManager
from core.agent import OTTOAgent

def main():
    """Função principal do chat interativo."""
    print("\n" + "=" * 50)
    print("🤖 OTTO - Assistente Educacional (Chat Interativo)")
    print("=" * 50)
    print("Digite 'sair' para encerrar.")
    print("Digite 'limpar' para limpar o histórico de conversa.")
    print("=" * 50 + "\n")
    
    # Inicializar componentes
    try:
        print("Inicializando componentes...")
        llm_manager = LLMManager()
        vector_store_manager = VectorStoreManager()
        memory_manager = MemoryManager()
        
        # Inicializar agente
        agent = OTTOAgent(llm_manager, vector_store_manager, memory_manager)
            
        # Nome de usuário para o chat
        user_id = input("Digite seu nome: ")
        if not user_id:
            user_id = "usuario"
        
        print(f"\nOlá, {user_id}! Como posso ajudar você hoje?")
        
        # Loop principal
        while True:
            # Obter pergunta do usuário
            query = input("\nPergunta: ")
            
            # Verificar comandos especiais
            if query.lower() == "sair":
                print("\nAté a próxima! 👋")
                break
            
            if query.lower() == "limpar":
                memory_manager.clear_history(user_id)
                print("\nHistórico de conversa limpo.")
                continue
            
            # Processar pergunta
            print("\nProcessando...")
            response = agent.process_query(query, user_id=user_id)
            
            # Mostrar resposta
            print("\nResposta:")
            print(response)
            
    except Exception as e:
        print(f"\nErro ao inicializar o chat: {e}")

if __name__ == "__main__":
    main()
