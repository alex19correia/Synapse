from dotenv import load_dotenv
import os
import redis
from github import Github
from src.config.settings import get_settings

def test_config():
    """Testa configurações básicas do ambiente"""
    load_dotenv()
    settings = get_settings()
    
    print("\n🔍 Testando Configurações...")
    
    # Testa GitHub Token
    try:
        g = Github(settings.github_token)
        user = g.get_user()
        print(f"✅ GitHub: Conectado como {user.login}")
    except Exception as e:
        print(f"❌ GitHub: Erro - {str(e)}")
    
    # Testa Redis
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        print("✅ Redis: Conectado")
    except Exception as e:
        print(f"❌ Redis: Erro - {str(e)}")

if __name__ == "__main__":
    test_config() 