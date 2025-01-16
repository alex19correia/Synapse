from pathlib import Path
import json
from typing import Dict, Any
from datetime import datetime
import os

class UserService:
    def __init__(self):
        self.user_data_path = Path("data/user")
        self.user_data_path.mkdir(parents=True, exist_ok=True)
        self.user_data = self._load_user_data()
        
    def _load_user_data(self) -> Dict:
        """Carrega dados do usuário"""
        data_file = self.user_data_path / "profile.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_user_data(self):
        """Salva dados do usuário"""
        with open(self.user_data_path / "profile.json", 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, indent=2, ensure_ascii=False)
    
    def update_user_info(self, key: str, value: Any):
        """Atualiza informação do usuário"""
        self.user_data[key] = value
        self.user_data["last_updated"] = datetime.now().isoformat()
        self.save_user_data()
    
    def get_user_info(self, key: str = None) -> Any:
        """Obtém informação do usuário"""
        if key is None:
            return self.user_data
        return self.user_data.get(key)
    
    def collect_system_info(self):
        """Coleta informações básicas do sistema"""
        self.update_user_info("username", os.getlogin())
        self.update_user_info("home_dir", str(Path.home()))
        # Adicionar mais coletas conforme necessário 