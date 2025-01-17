from langfuse.client import Langfuse
from typing import Dict, Any

class LoggingService:
    def __init__(self, config: Dict[str, Any]):
        self.langfuse = Langfuse(
            public_key=config["LANGFUSE_PUBLIC_KEY"],
            secret_key=config["LANGFUSE_SECRET_KEY"],
            host=config.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
    
    async def log_llm_interaction(self, trace_id: str, prompt: str, response: str, metadata: Dict[str, Any]):
        """Log de interações com LLMs"""
        try:
            self.langfuse.trace(
                trace_id=trace_id,
                name="llm_interaction",
                metadata={
                    "prompt": prompt,
                    "response": response,
                    **metadata
                }
            )
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
            # TODO: Implementar fallback logging 