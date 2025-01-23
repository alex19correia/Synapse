import asyncio
from redis.asyncio import Redis
from loguru import logger

async def test_redis_connection():
    """Testa a conexão com o Redis."""
    try:
        # Inicializa o cliente Redis
        redis = Redis(
            host="localhost",
            port=6380,
            decode_responses=True
        )
        
        # Testa a conexão
        logger.info("🔄 Testando conexão com Redis...")
        await redis.ping()
        logger.info("✅ Conexão com Redis estabelecida!")
        
        # Testa operações básicas
        logger.info("🔄 Testando operações básicas...")
        test_key = "test_key"
        test_value = "test_value"
        
        # Set
        await redis.set(test_key, test_value)
        logger.info("✅ SET bem sucedido!")
        
        # Get
        value = await redis.get(test_key)
        assert value == test_value
        logger.info("✅ GET bem sucedido!")
        
        # Delete
        await redis.delete(test_key)
        logger.info("✅ DELETE bem sucedido!")
        
        logger.info("✨ Todos os testes passaram!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar Redis: {e}")
        raise
    finally:
        await redis.aclose()

if __name__ == "__main__":
    asyncio.run(test_redis_connection()) 