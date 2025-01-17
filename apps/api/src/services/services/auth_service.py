from src.services.metrics_service import metrics_service

class AuthService:
    def __init__(self):
        self.active_users = set()
    
    async def login(self, user_id: str):
        self.active_users.add(user_id)
        metrics_service.set_active_users(len(self.active_users))
    
    async def logout(self, user_id: str):
        self.active_users.discard(user_id)
        metrics_service.set_active_users(len(self.active_users)) 