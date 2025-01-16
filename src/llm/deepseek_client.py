"""Cliente para a API do DeepSeek."""
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
from pydantic import BaseModel

from ..config.settings import get_settings
from ..analytics.metrics.llm_metrics import LLMMetrics
from ..core.cache import CacheService

class DeepSeekMessage(BaseModel):
    """Mensagem para o DeepSeek."""
    role: str
    content: str
    name: Optional[str] = None

class DeepSeekResponse(BaseModel):
    """Resposta do DeepSeek."""
    content: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    cached: bool = False

class Entity(BaseModel):
    """Entidade extraída do texto."""
    text: str
    type: str
    start: int
    end: int

class DeepSeekClient:
    """Cliente para a API do DeepSeek."""
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.MODEL_NAME
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        self.cache = CacheService(settings.REDIS_URL)
        self.metrics = LLMMetrics()
        self._cache_lock = asyncio.Lock()
    
    def _get_cache_key(self, messages: List[DeepSeekMessage], **kwargs) -> str:
        """Gera uma chave de cache para as mensagens e parâmetros."""
        # Include message data with all fields
        msg_data = [
            {
                "role": m.role,
                "content": m.content,
                **({"name": m.name} if m.name else {})
            } 
            for m in messages
        ]
        
        # Include generation parameters in cache key
        params = {
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p"),
            "presence_penalty": kwargs.get("presence_penalty"),
            "frequency_penalty": kwargs.get("frequency_penalty"),
            "stop": kwargs.get("stop"),
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        # Create a readable key for testing
        key_parts = [
            "deepseek:response",
            ":".join(f"{k}={v}" for k, v in sorted(params.items())),
            ":".join(
                f"{m['role']}={m['content']}" + (f":name={m['name']}" if 'name' in m else "")
                for m in msg_data
            )
        ]
        return ":".join(key_parts)
    
    def _validate_cached_data(self, data: Dict[str, Any]) -> bool:
        """Validates cached data structure."""
        required_fields = {"content", "finish_reason", "usage", "cached"}
        return (
            isinstance(data, dict) 
            and all(field in data for field in required_fields)
            and isinstance(data["content"], str)
            and data["content"]  # Not empty
            and (data["usage"] is None or isinstance(data["usage"], dict))
        )
    
    async def generate_with_cache(
        self,
        messages: List[DeepSeekMessage],
        **kwargs
    ) -> DeepSeekResponse:
        """Gera uma resposta com cache."""
        cache_key = self._get_cache_key(messages, **kwargs)
        
        # Try to get from cache first
        try:
            cached_data = await self.cache.get(cache_key)
            if cached_data and self._validate_cached_data(cached_data):
                # Check TTL
                ttl = await self.cache.ttl(cache_key)
                if ttl is None or ttl > 60:  # More than 1 minute left or no TTL
                    await self.metrics.track_cache_operation("generate", hit=True)
                    return DeepSeekResponse(**cached_data)
                
            await self.metrics.track_cache_operation("generate", hit=False)
            
            # Use lock for cache operations to prevent race conditions
            async with self._cache_lock:
                # Double-check cache in case another process set it
                cached_data = await self.cache.get(cache_key)
                if cached_data and self._validate_cached_data(cached_data):
                    ttl = await self.cache.ttl(cache_key)
                    if ttl is None or ttl > 60:  # More than 1 minute left or no TTL
                        await self.metrics.track_cache_operation("generate", hit=True)
                        return DeepSeekResponse(**cached_data)
                
                # Generate response
                start_time = time.time()
                await self.metrics.start_request()
                
                try:
                    response = await self.generate(messages, **kwargs)
                    
                    # Track successful request
                    await self.metrics.track_request(
                        operation="generate",
                        status="success",
                        latency=time.time() - start_time
                    )
                    
                    # Prepare cache data
                    response_data = {
                        "content": response.content,
                        "finish_reason": response.finish_reason,
                        "usage": response.usage,
                        "cached": True
                    }
                    
                    # Save to cache with TTL
                    if self._validate_cached_data(response_data):
                        await self.cache.set(
                            cache_key,
                            response_data,
                            ttl=3600  # 1 hour
                        )
                    
                    # Return uncached response
                    return DeepSeekResponse(
                        content=response.content,
                        finish_reason=response.finish_reason,
                        usage=response.usage,
                        cached=False
                    )
                    
                except Exception as e:
                    await self.metrics.track_request(
                        operation="generate",
                        status="error",
                        latency=time.time() - start_time
                    )
                    raise e
                
                finally:
                    await self.metrics.end_request()
                    
        except Exception as e:
            # If Redis fails, fallback to direct generation
            await self.metrics.track_cache_operation("generate", hit=False)
            return await self.generate(messages, **kwargs)
    
    async def generate_with_retry(
        self,
        messages: List[DeepSeekMessage],
        max_retries: int = 3,
        **kwargs
    ) -> DeepSeekResponse:
        """Gera uma resposta com retry."""
        last_error = None
        for attempt in range(max_retries):
            try:
                return await self.generate(messages, **kwargs)
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    raise last_error
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Should never reach here, but just in case
        raise last_error if last_error else Exception("Unknown error in retry logic")
    
    async def generate(
        self,
        messages: List[DeepSeekMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False
    ) -> DeepSeekResponse:
        """Gera uma resposta do DeepSeek."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": m.role,
                            "content": m.content,
                            **({"name": m.name} if m.name else {})
                        }
                        for m in messages
                    ],
                    "temperature": temperature or self.temperature,
                    "max_tokens": max_tokens or self.max_tokens,
                    **({"top_p": top_p} if top_p is not None else {}),
                    **({"presence_penalty": presence_penalty} if presence_penalty is not None else {}),
                    **({"frequency_penalty": frequency_penalty} if frequency_penalty is not None else {}),
                    **({"stop": stop} if stop else {}),
                    "stream": stream
                }
            )
            response.raise_for_status()
            data = await response.json()
            
            return DeepSeekResponse(
                content=data["choices"][0]["message"]["content"],
                finish_reason=data["choices"][0].get("finish_reason"),
                usage=data.get("usage")
            )
    
    async def stream_generate(
        self,
        messages: List[DeepSeekMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Gera uma resposta em streaming."""
        kwargs["stream"] = True
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": m.role,
                            "content": m.content,
                            **({"name": m.name} if m.name else {})
                        }
                        for m in messages
                    ],
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "stream": True
                },
                stream=True
            )
            response.raise_for_status()
            
            # Aguarda o iterador
            aiter_lines = await response.aiter_lines()
            async for line in aiter_lines:
                if line.strip():
                    data = json.loads(line.replace("data: ", ""))
                    if token := data["choices"][0].get("delta", {}).get("content"):
                        yield token
    
    async def summarize(
        self,
        text: str,
        max_length: int = 200
    ) -> str:
        """Gera um resumo do texto."""
        messages = [
            DeepSeekMessage(
                role="system",
                content="Você é um assistente especializado em resumir textos."
            ),
            DeepSeekMessage(
                role="user",
                content=f"Resuma o seguinte texto em no máximo {max_length} caracteres:\n\n{text}"
            )
        ]
        
        response = await self.generate_with_cache(messages)
        return response.content
    
    async def extract_entities(
        self,
        text: str
    ) -> List[Entity]:
        """Extrai entidades do texto."""
        messages = [
            DeepSeekMessage(
                role="system",
                content="Você é um assistente especializado em extrair entidades de textos. Retorne apenas um array JSON com as entidades encontradas, no formato: [{text: string, type: string, start: number, end: number}]"
            ),
            DeepSeekMessage(
                role="user",
                content=f"Extraia as entidades do seguinte texto:\n\n{text}"
            )
        ]
        
        response = await self.generate_with_cache(messages)
        entities = json.loads(response.content)
        return [Entity(**entity) for entity in entities] 