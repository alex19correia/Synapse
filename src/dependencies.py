from fastapi import Depends
from redis.asyncio import Redis
from loguru import logger
import os

from .config import Settings, get_settings
from .services.message_service import MessageService
from .services.chat_service import ChatService
from .services.llm_service import LLMService
from .core.cache import CacheService
from .config.llm_config import LLMConfig

def is_test_environment() -> bool:
    """Verifica se está em ambiente de teste."""
    return os.getenv("ENVIRONMENT") == "test"

async def get_redis_client(settings: Settings = Depends(get_settings)) -> Redis:
    """
    Retorna uma instância do cliente Redis.
    """
    logger.debug(f"🔄 Inicializando cliente Redis: {settings.redis_host}:{settings.redis_port}")
    
    try:
        redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=0,
            decode_responses=True
        )
        
        # Testa a conexão
        logger.debug("🔍 Testando conexão com Redis...")
        await redis.ping()
        logger.info("✅ Conexão com Redis estabelecida")
        
        return redis
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com Redis: {str(e)}")
        logger.exception(e)
        raise e

async def get_cache_service(redis: Redis = Depends(get_redis_client)) -> CacheService:
    """
    Retorna uma instância do CacheService.
    """
    logger.debug("🔄 Inicializando CacheService...")
    service = CacheService(redis)
    logger.debug("✅ CacheService inicializado")
    return service

def get_llm_config() -> LLMConfig:
    """
    Retorna uma instância do LLMConfig.
    """
    logger.debug("🔄 Carregando configuração do LLM...")
    config = LLMConfig()
    logger.debug(f"✅ Configuração carregada: {config}")
    return config

async def get_llm_service(
    cache_service: CacheService = Depends(get_cache_service),
    config: LLMConfig = Depends(get_llm_config)
) -> LLMService:
    """
    Retorna uma instância do LLMService.
    """
    logger.debug("🔄 Inicializando LLMService...")
    service = LLMService(cache_service=cache_service, config=config)
    logger.debug("✅ LLMService inicializado")
    return service

def get_message_service() -> MessageService:
    """
    Retorna uma instância do MessageService.
    """
    logger.debug("🔄 Inicializando MessageService...")
    service = MessageService()
    logger.debug("✅ MessageService inicializado")
    return service

async def get_chat_service(
    message_service: MessageService = Depends(get_message_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> ChatService:
    """
    Retorna uma instância do ChatService.
    """
    logger.debug("🔄 Inicializando ChatService...")
    service = ChatService(message_service=message_service, llm_service=llm_service)
    logger.debug("✅ ChatService inicializado")
    return service 