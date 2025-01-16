import logging
import sys
from typing import Optional
from pathlib import Path

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Retorna um logger configurado com o nome especificado.
    
    Args:
        name: Nome do logger
        level: Nível de logging (opcional)
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configura o formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para arquivo
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"{name}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Define o nível de logging
        logger.setLevel(level or logging.INFO)
    
    return logger

# Logger padrão
logger = get_logger("synapse") 