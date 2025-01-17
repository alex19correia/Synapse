"""LLM service implementation."""
from typing import List, Dict, Optional
from loguru import logger
from fastapi import HTTPException
import httpx
from datetime import datetime

class LLMService:
    """Service to handle LLM interactions."""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        """Initialize LLM service."""
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        logger.debug(f"🤖 LLMService initialized with model {model}")
    
    async def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Get a chat completion from the LLM."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.debug(f"🚀 Sending request to LLM with {len(messages)} messages")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"LLM API error: {response.text}"
                    )
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.debug("✅ Received response from LLM")
                
                return content
                
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"❌ Error getting LLM completion: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get response from LLM"
            )
    
    def format_chat_history(
        self,
        messages: List[Dict],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Format chat history for the LLM API."""
        formatted_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Format chat messages
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted_messages 