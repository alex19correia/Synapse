import asyncio
from redis.asyncio import Redis
from src.config import get_settings

async def test_redis_connection():
    """Testa a conexão com Redis"""
    print("\n🔍 Testando conexão com Redis...")
    
    settings = get_settings()
    try:
        redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True
        )
        
        # Testa conexão
        await redis.ping()
        print("✅ Redis: Conexão estabelecida com sucesso!")
        
        # Testa operações básicas
        await redis.set("test_key", "test_value")
        value = await redis.get("test_key")
        print(f"✅ Redis: Operações básicas funcionando (test_key = {value})")
        
        # Limpa chave de teste
        await redis.delete("test_key")
        
    except Exception as e:
        print(f"❌ Redis: Erro na conexão - {str(e)}")
    finally:
        await redis.aclose()

if __name__ == "__main__":
    asyncio.run(test_redis_connection()) 