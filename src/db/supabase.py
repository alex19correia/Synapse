from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from pydantic import BaseModel

class CrawlMetadata(BaseModel):
    """Metadados de um crawl"""
    url: str
    status: str
    timestamp: datetime
    duration: float
    content_size: int
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class SupabaseClient:
    """Cliente Supabase para persistência"""
    
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
    
    async def save_crawl(self, metadata: CrawlMetadata) -> None:
        """Salva metadados de um crawl"""
        data = metadata.dict()
        data["timestamp"] = data["timestamp"].isoformat()
        
        await self.client.table("crawls").insert(data).execute()
    
    async def get_crawl_history(self, url: str) -> list:
        """Recupera histórico de crawls para uma URL"""
        response = await self.client.table("crawls") \
            .select("*") \
            .eq("url", url) \
            .order("timestamp", desc=True) \
            .execute()
            
        return response.data
    
    async def save_config(self, name: str, config: Dict[str, Any]) -> None:
        """Salva uma configuração"""
        data = {
            "name": name,
            "config": config,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await self.client.table("configs") \
            .upsert(data, on_conflict="name") \
            .execute()
    
    async def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Recupera uma configuração"""
        response = await self.client.table("configs") \
            .select("config") \
            .eq("name", name) \
            .limit(1) \
            .execute()
            
        if response.data:
            return response.data[0]["config"]
        return None 