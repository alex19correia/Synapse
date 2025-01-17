from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
import re

def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formata um objeto datetime para string."""
    return dt.strftime(format)

def parse_datetime(dt_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Converte uma string para objeto datetime."""
    return datetime.strptime(dt_str, format)

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extrai entidades de um texto (nomes, datas, locais, etc.).
    Implementação básica usando regex.
    """
    entities = {
        "dates": [],
        "times": [],
        "emails": [],
        "urls": []
    }
    
    # Extrair datas (formato DD/MM/YYYY ou YYYY-MM-DD)
    date_patterns = [
        r"\d{2}/\d{2}/\d{4}",
        r"\d{4}-\d{2}-\d{2}"
    ]
    for pattern in date_patterns:
        entities["dates"].extend(re.findall(pattern, text))
    
    # Extrair horários (formato HH:MM ou HH:MM:SS)
    time_patterns = [
        r"\d{2}:\d{2}(:\d{2})?",
        r"\d{1,2}h\d{2}"
    ]
    for pattern in time_patterns:
        entities["times"].extend(re.findall(pattern, text))
    
    # Extrair emails
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    entities["emails"] = re.findall(email_pattern, text)
    
    # Extrair URLs
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    entities["urls"] = re.findall(url_pattern, text)
    
    return entities

def sanitize_input(text: str) -> str:
    """Remove caracteres especiais e sanitiza input do utilizador."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Remove caracteres especiais, mantendo pontuação básica
    text = re.sub(r"[^\w\s.,!?@-]", "", text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca um texto para o tamanho máximo especificado."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Carrega uma string JSON de forma segura."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default 