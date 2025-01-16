from typing import Dict, List, Optional
from pydantic import BaseModel
from src.core.memory import MemoryManager

class Example(BaseModel):
    """Exemplo de uso do sistema."""
    title: str
    description: str
    code: str
    output: Optional[str]
    tags: List[str]

class ExampleManager:
    """Gestor de exemplos do sistema."""
    
    def __init__(self, memory: MemoryManager):
        self.memory = memory
        self._examples: Dict[str, Example] = {}
    
    async def add_example(self, example: Example):
        """Adiciona novo exemplo."""
        key = f"example:{example.title}"
        await self.memory.store(key, example.dict())
        self._examples[example.title] = example
    
    async def get_examples(
        self,
        tags: Optional[List[str]] = None
    ) -> List[Example]:
        """Recupera exemplos filtrados por tags."""
        if not tags:
            return list(self._examples.values())
            
        return [
            example for example in self._examples.values()
            if any(tag in example.tags for tag in tags)
        ]
    
    async def generate_example(
        self,
        feature: str,
        complexity: str = "basic"
    ) -> Example:
        """Gera exemplo automaticamente."""
        # Implementar geração automática de exemplos
        pass 