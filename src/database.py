"""
Database connection and operations.
"""
from typing import Optional, Dict, Any
from supabase import create_client, Client
from src.config.settings import get_settings

class Database:
    """Database connection and operations."""
    
    def __init__(self):
        """Initialize database connection."""
        self.settings = get_settings()
        self.client: Optional[Client] = None
        
    def _connect(self) -> Client:
        """Connect to database."""
        if self.client:
            return self.client
            
        # For testing purposes, return a mock client
        if self.settings.ENV == "test":
            class MockClient:
                def __init__(self):
                    self.data = {}
                    
                def table(self, name: str):
                    return self
                    
                def insert(self, data: Dict[str, Any]):
                    self.data = data
                    return {"data": data, "error": None}
                    
                def select(self, *args):
                    return self
                    
                def execute(self):
                    return {"data": [self.data], "error": None}
                    
            self.client = MockClient()
            return self.client
            
        # For production, connect to Supabase
        if not self.settings.SUPABASE_URL or not self.settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and key are required")
            
        try:
            self.client = create_client(
                self.settings.SUPABASE_URL,
                self.settings.SUPABASE_KEY
            )
            return self.client
        except Exception as e:
            if self.settings.ENV == "test":
                # Fallback to mock client in test mode
                self.client = MockClient()
                return self.client
            raise
        
    def get_client(self) -> Client:
        """Get database client."""
        if not self.client:
            self.client = self._connect()
        return self.client

# Create singleton instance
db = Database() 