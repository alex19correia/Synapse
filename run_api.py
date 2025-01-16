import uvicorn
from loguru import logger

if __name__ == "__main__":
    # Configurar logger
    logger.add(
        "logs/synapse.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO"
    )
    
    # Iniciar servidor
    logger.info("🚀 A iniciar servidor Synapse...")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Apenas em desenvolvimento
    ) 