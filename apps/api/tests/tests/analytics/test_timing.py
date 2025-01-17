from posthog import Posthog
from datetime import datetime

# Configuração do PostHog
posthog = Posthog(
    project_api_key='phc_FfrnE3gAla60Fcnj16QbpRtyNP3Nk5J92MJLUjZMaU9',
    host='https://eu.i.posthog.com'
)

def test_timing():
    """Teste com timing correto"""
    
    # Enviar evento com timing
    posthog.capture(
        distinct_id='test_user_1',
        event='llm_request',
        properties={
            '$time': datetime.now().isoformat(),
            'duration': 1.5,  # Tente com 'duration' em vez de 'response_time'
            'timing': 1.5,    # E também com 'timing'
            'model': 'claude-3-sonnet'
        }
    )
    
    print("✅ Evento com timing enviado!")

if __name__ == "__main__":
    test_timing() 