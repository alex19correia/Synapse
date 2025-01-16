from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json
from rich.console import Console
from pydantic import BaseModel
from .rag import RAGSystem

console = Console()

class Memory(BaseModel):
    """Sistema de memória do Synapse"""
    
    core_beliefs: Dict[str, str] = {
        "identity": "Sou o Synapse, um assistente virtual pessoal focado em ajudar no desenvolvimento",
        "purpose": "Meu objetivo é ser a entidade que melhor conhece e ajuda o utilizador",
        "values": "Privacidade, transparência e crescimento contínuo são minhas prioridades"
    }
    
    episodic_memory: List[Dict] = []
    semantic_memory: Dict[str, Dict] = {}
    memory_file: Path = Path.home() / ".synapse_memory.json"
    
    def __init__(self):
        """Inicializa ou carrega memória existente"""
        super().__init__()
        self.rag = RAGSystem()
        self.load_memory()
    
    def load_memory(self):
        """Carrega memória do arquivo"""
        try:
            if self.memory_file.exists():
                data = json.loads(self.memory_file.read_text())
                self.episodic_memory = data.get("episodic", [])
                self.semantic_memory = data.get("semantic", {})
                console.print("[info]Memória carregada com sucesso[/info]")
            else:
                self.save_memory()
                console.print("[info]Nova memória inicializada[/info]")
        except Exception as e:
            console.print(f"[error]Erro ao carregar memória: {e}[/error]")
    
    def save_memory(self):
        """Salva memória no arquivo"""
        try:
            data = {
                "episodic": self.episodic_memory,
                "semantic": self.semantic_memory
            }
            self.memory_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            console.print(f"[error]Erro ao salvar memória: {e}[/error]")
    
    async def add_experience(self, event_type: str, details: Dict):
        """Adiciona nova experiência à memória episódica e RAG"""
        # Adicionar à memória episódica
        experience = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        self.episodic_memory.append(experience)
        
        # Indexar no RAG
        text = json.dumps(details)  # Converter detalhes em texto
        await self.rag.index_document(text, {"type": event_type})
        
        self.save_memory()
    
    def learn_concept(self, category: str, concept: str, details: Dict):
        """Adiciona novo conhecimento à memória semântica"""
        if category not in self.semantic_memory:
            self.semantic_memory[category] = {}
        
        self.semantic_memory[category][concept] = {
            "details": details,
            "learned_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        self.save_memory()
    
    def recall_experiences(self, event_type: Optional[str] = None) -> List[Dict]:
        """Recupera experiências da memória episódica"""
        if event_type:
            return [e for e in self.episodic_memory if e["type"] == event_type]
        return self.episodic_memory
    
    def recall_concept(self, category: str, concept: str) -> Optional[Dict]:
        """Recupera conhecimento da memória semântica"""
        if category in self.semantic_memory and concept in self.semantic_memory[category]:
            info = self.semantic_memory[category][concept]
            info["last_accessed"] = datetime.now().isoformat()
            self.save_memory()
            return info
        return None 
    
    async def get_relevant_context(self, query: str) -> str:
        """Recupera contexto relevante usando RAG"""
        return await self.rag.get_context(query) 