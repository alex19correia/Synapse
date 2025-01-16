from typing import Optional
import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """Valida um endereço de email."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_password(password: str, min_length: int = 8) -> tuple[bool, str]:
    """
    Valida uma senha.
    
    Args:
        password: Senha a ser validada
        min_length: Comprimento mínimo da senha
        
    Returns:
        Tupla (válido, mensagem)
    """
    if len(password) < min_length:
        return False, f"A senha deve ter pelo menos {min_length} caracteres"
        
    if not re.search(r"[A-Z]", password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
        
    if not re.search(r"[a-z]", password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
        
    if not re.search(r"\d", password):
        return False, "A senha deve conter pelo menos um número"
        
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "A senha deve conter pelo menos um caractere especial"
        
    return True, "Senha válida"

def validate_date(date_str: str, format: str = "%Y-%m-%d") -> tuple[bool, Optional[datetime]]:
    """
    Valida uma data.
    
    Args:
        date_str: String da data
        format: Formato esperado
        
    Returns:
        Tupla (válido, objeto datetime ou None)
    """
    try:
        date_obj = datetime.strptime(date_str, format)
        return True, date_obj
    except ValueError:
        return False, None

def validate_phone(phone: str) -> bool:
    """Valida um número de telefone (formato português)."""
    # Remove espaços e caracteres especiais
    phone = re.sub(r"[\s\-\(\)]", "", phone)
    
    # Verifica se começa com +351 ou 00351 (opcional)
    phone = re.sub(r"^(\+351|00351)", "", phone)
    
    # Verifica se tem 9 dígitos e começa com 9, 2 ou 3
    pattern = r"^[923]\d{8}$"
    return bool(re.match(pattern, phone))

def validate_url(url: str) -> bool:
    """Valida uma URL."""
    pattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$"
    return bool(re.match(pattern, url))

def validate_text_length(text: str, min_length: int = 0, max_length: int = 1000) -> tuple[bool, str]:
    """
    Valida o comprimento de um texto.
    
    Args:
        text: Texto a ser validado
        min_length: Comprimento mínimo
        max_length: Comprimento máximo
        
    Returns:
        Tupla (válido, mensagem)
    """
    length = len(text)
    
    if length < min_length:
        return False, f"O texto deve ter pelo menos {min_length} caracteres"
        
    if length > max_length:
        return False, f"O texto deve ter no máximo {max_length} caracteres"
        
    return True, "Texto válido" 