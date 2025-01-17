from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class Role(BaseModel):
    name: str
    permissions: List[Permission]
    scope: Optional[str] = None

class PermissionSystem:
    """Sistema de gestão de permissões."""
    
    def __init__(self):
        self._roles: Dict[str, Role] = {}
        self._user_roles: Dict[str, List[str]] = {}
        self._setup_default_roles()
    
    async def check_permission(
        self,
        user_id: str,
        required_permission: Permission,
        scope: Optional[str] = None
    ) -> bool:
        """Verifica se usuário tem permissão."""
        user_roles = self._user_roles.get(user_id, [])
        
        for role_name in user_roles:
            role = self._roles.get(role_name)
            if not role:
                continue
                
            if required_permission in role.permissions:
                if not scope or not role.scope or scope == role.scope:
                    return True
        
        return False
    
    async def assign_role(self, user_id: str, role_name: str):
        """Atribui role ao usuário."""
        if role_name not in self._roles:
            raise ValueError(f"Role {role_name} não existe")
            
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
            
        if role_name not in self._user_roles[user_id]:
            self._user_roles[user_id].append(role_name)
    
    def _setup_default_roles(self):
        """Configura roles padrão."""
        self._roles = {
            "admin": Role(
                name="admin",
                permissions=[p for p in Permission]
            ),
            "user": Role(
                name="user",
                permissions=[Permission.READ, Permission.EXECUTE]
            ),
            "viewer": Role(
                name="viewer",
                permissions=[Permission.READ]
            )
        } 