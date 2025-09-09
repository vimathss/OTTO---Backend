"""
Memory Manager - Gerenciador de memória conversacional para o OTTO

Este módulo gerencia o histórico de conversas e contexto entre sessões,
permitindo que o assistente mantenha o contexto das interações com os usuários.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class MemoryManager:
    """Gerencia o histórico de conversas e contexto entre sessões."""
    
    def __init__(self, memory_dir: str = "./memory", max_turns: int = 10):
        self.memory_dir = memory_dir
        self.max_turns = max_turns
        self.conversations = {}
        
        # Garantir que o diretório existe
        os.makedirs(memory_dir, exist_ok=True)
    
    def get_context(self, user_id: str) -> Dict[str, Any]:
        """Obtém o contexto da conversa para um usuário."""
        # Carregar conversa do disco se não estiver em memória
        if user_id not in self.conversations:
            self._load_conversation(user_id)
        
        # Formatar histórico para uso em prompts
        history_text = ""
        for exchange in self.conversations.get(user_id, []):
            history_text += f"Usuário: {exchange['question']}\n"
            history_text += f"Assistente: {exchange['answer']}\n\n"
        
        return {
            "conversation_history": history_text,
            "user_id": user_id,
            "exchanges": self.conversations.get(user_id, [])
        }
    
    def add_interaction(self, user_id: str, question: str, answer: str) -> None:
        """Adiciona uma interação ao histórico do usuário."""
        # Inicializar lista de conversas se necessário
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        # Adicionar nova interação
        self.conversations[user_id].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        
        # Manter apenas as últimas N interações
        if len(self.conversations[user_id]) > self.max_turns:
            self.conversations[user_id].pop(0)
        
        # Persistir no disco
        self._save_conversation(user_id)
    
    def clear_history(self, user_id: str) -> None:
        """Limpa o histórico de conversa de um usuário."""
        self.conversations[user_id] = []
        self._save_conversation(user_id)
    
    def _load_conversation(self, user_id: str) -> None:
        """Carrega conversa do disco."""
        file_path = os.path.join(self.memory_dir, f"{user_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.conversations[user_id] = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar conversa para {user_id}: {e}")
                self.conversations[user_id] = []
        else:
            self.conversations[user_id] = []
    
    def _save_conversation(self, user_id: str) -> None:
        """Salva conversa no disco."""
        file_path = os.path.join(self.memory_dir, f"{user_id}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversations[user_id], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar conversa para {user_id}: {e}")
