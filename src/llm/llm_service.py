"""LLM service module."""
from typing import Dict, Any, List, AsyncGenerator
import aiohttp
import json
import ssl
import certifi
from rich.console import Console
from src.config.settings import Settings

console = Console()

class LLMService:
    """LLM integration service."""
    
    def __init__(self, settings: Settings):
        """Initialize LLM service with settings."""
        self.client = LLMClient(settings)
        
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = None
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        try:
            return await self.client.complete(messages, model)
            
        except Exception as e:
            console.print(f"[error]LLM completion error: {str(e)}[/error]")
            raise
            
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion."""
        try:
            async for chunk in self.client.stream(messages, model):
                yield chunk
                
        except Exception as e:
            console.print(f"[error]LLM streaming error: {str(e)}[/error]")
            raise


class LLMClient:
    """LLM client implementation."""
    
    def __init__(self, settings: Settings):
        """Initialize LLM client."""
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = settings.DEFAULT_MODEL
        self.temperature = float(settings.TEMPERATURE)
        self.max_tokens = int(settings.MAX_TOKENS)
        
        # SSL context
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = None
    ) -> Dict[str, Any]:
        """Get completion from LLM."""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                formatted_messages = []
                for msg in messages:
                    if isinstance(msg, dict):
                        formatted_messages.append(msg)
                    else:
                        formatted_messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                
                payload = {
                    "model": model or self.model,
                    "messages": formatted_messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": False
                }
                
                console.print(f"[debug]Connecting to {self.api_url}/chat/completions[/debug]")
                console.print(f"[debug]Headers: {json.dumps(self.headers, indent=2)}[/debug]")
                console.print(f"[debug]Payload: {json.dumps(payload, indent=2)}[/debug]")
                
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30  # Added timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        console.print(f"[error]DeepSeek API error (Status {response.status}): {error_text}[/error]")
                        raise Exception(f"DeepSeek API error: {error_text}")
                        
                    result = await response.json()
                    console.print(f"[debug]Response: {json.dumps(result, indent=2)}[/debug]")
                    return {
                        "response": result["choices"][0]["message"]["content"],
                        "usage": result.get("usage", {})
                    }
                    
        except aiohttp.ClientError as e:
            console.print(f"[error]Connection error: {str(e)}[/error]")
            raise
        except Exception as e:
            console.print(f"[error]Unexpected error: {str(e)}[/error]")
            raise

    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """Stream completion from LLM.
        
        Args:
            messages: List of messages
            model: Optional model override
            
        Yields:
            Completion chunks
            
        Raises:
            Exception: If streaming fails
        """
        async with aiohttp.ClientSession() as session:
            # Convert messages to list of dicts
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    formatted_messages.append(msg)
                else:
                    formatted_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            payload = {
                "model": model or self.model,
                "messages": formatted_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True
            }
            
            async with session.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error: {error_text}")
                    
                async for line in response.content:
                    if line:
                        chunk = line.decode().strip()
                        if chunk.startswith("data: "):
                            chunk = chunk[6:]  # Remove "data: " prefix
                            if chunk != "[DONE]":
                                try:
                                    result = json.loads(chunk)
                                    content = result["choices"][0]["delta"].get("content")
                                    if content:
                                        yield content
                                except Exception as e:
                                    console.print(f"[error]Error parsing chunk: {e}[/error]")