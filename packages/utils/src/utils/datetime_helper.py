from datetime import datetime
import locale
from typing import Dict

def get_datetime_info() -> Dict[str, str]:
    # Configurar locale para português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese')
        except:
            pass  # Se falhar, usa o locale padrão

    now = datetime.now()
    
    # Formatar data e hora em português
    data = now.strftime("%d de %B de %Y")
    dia_semana = now.strftime("%A")
    hora = now.strftime("%H:%M")
    
    return {
        "data": data,
        "dia_semana": dia_semana.capitalize(),
        "hora": hora
    } 