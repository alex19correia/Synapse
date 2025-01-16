from posthog import Posthog
import os
from datetime import datetime

# Configuração do PostHog
posthog = Posthog(
    project_api_key='phc_FfrnE3gAla60Fcnj16QbpRtyNP3Nk5J92MJLUjZMaU9',
    host='https://eu.i.posthog.com'  # Note o host específico para EU
)

def test_synapse_events():
    """Testa eventos principais do Synapse"""
    
    # ID de teste do usuário
    test_user = "test_user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Evento de Chat/Mensagem
    posthog.capture(
        distinct_id=test_user,
        event='message_sent',
        properties={
            'message_type': 'user_query',
            'timestamp': datetime.now().isoformat(),
            'environment': 'test'
        }
    )
    print("✅ Evento message_sent enviado")

    # 2. Evento de LLM Request
    posthog.capture(
        distinct_id=test_user,
        event='llm_request',
        properties={
            'model': 'claude-3-sonnet',
            'tokens': 250,
            'response_time': 1.5,
            'cache_hit': False,
            'environment': 'test'
        }
    )
    print("✅ Evento llm_request enviado")

    # 3. Evento de Cache
    posthog.capture(
        distinct_id=test_user,
        event='cache_operation',
        properties={
            'operation': 'get',
            'success': True,
            'latency': 0.05,
            'environment': 'test'
        }
    )
    print("✅ Evento cache_operation enviado")

if __name__ == "__main__":
    test_synapse_events()
    print("\n🎉 Todos os eventos de teste foram enviados!") 