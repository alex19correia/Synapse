from pydantic import BaseModel
from typing import Dict, Any

class OllamaConfig(BaseModel):
    """Configuração do Ollama para melhor performance"""
    
    # Configurações do modelo
    model_name: str = "codellama"
    model_type: str = "completion"
    
    # Recursos
    gpu_layers: int = -1  # -1 = usar todas as camadas na GPU se disponível
    num_threads: int = 4
    num_ctx: int = 2048
    
    # Parâmetros de geração
    temperature: float = 0.1
    top_k: int = 10
    top_p: float = 0.3
    repeat_penalty: float = 1.1
    
    # Sistema
    timeout: float = 15.0
    max_retries: int = 2
    retry_delay: float = 1.0
    
    # Cache
    cache_enabled: bool = True
    cache_capacity: int = 2000  # Número de respostas em cache
    
    def get_request_params(self) -> Dict[str, Any]:
        """Retorna parâmetros formatados para request"""
        return {
            "model": self.model_name,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "num_gpu": 1 if self.gpu_layers != 0 else 0,
                "num_thread": self.num_threads,
                "top_k": self.top_k,
                "top_p": self.top_p,
                "repeat_penalty": self.repeat_penalty,
                "stop": ["</s>", "Human:", "Assistant:"]
            }
        } 