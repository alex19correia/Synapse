import uvicorn
from loguru import logger
from .config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    # Configurar logger
    logger.add(
        "logs/synapse.log",
        rotation="500 MB",
        retention="10 days",
        level=settings.log_level
    )
    
    # Iniciar servidor
    logger.info("🚀 A iniciar servidor Synapse...")
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True  # Apenas em desenvolvimento
    ) 