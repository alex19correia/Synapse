from typing import List, Optional
from datetime import datetime

class ConversationMemory:
    def __init__(self, max_history: int = 1000):
        self.conversation_history = []
        self.max_history = max_history
        
    def add_memory(self, message: str, metadata: Optional[dict] = None):
        """Adiciona uma nova memória ao histórico"""
        memory = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.conversation_history.append(memory)
        
        # Limita o tamanho do histórico
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
            
    def get_history(self, limit: Optional[int] = None) -> List[dict]:
        """Retorna o histórico de conversas"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history
        
    def clear(self):
        """Limpa o histórico de conversas"""
        self.conversation_history = []
        
    def search(self, query: str) -> List[dict]:
        """Busca por mensagens no histórico que contenham a query"""
        return [
            memory for memory in self.conversation_history 
            if query.lower() in memory['message'].lower()
        ] 