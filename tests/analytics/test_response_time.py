from posthog import Posthog
from datetime import datetime
import time

# Configuração do PostHog
posthog = Posthog(
    project_api_key='phc_FfrnE3gAla60Fcnj16QbpRtyNP3Nk5J92MJLUjZMaU9',
    host='https://eu.i.posthog.com'
)

def test_response_time():
    """Teste focado apenas em response_time"""
    
    # Simular 3 chamadas LLM com tempos diferentes
    response_times = [1.5, 2.0, 2.5]  # tempos em segundos
    
    for rt in response_times:
        event = {
            'event': 'llm_request',
            'properties': {
                'response_time': rt,
                'model': 'claude-3-sonnet',
                '$time': datetime.now().isoformat()
            }
        }
        
        # Enviar evento
        posthog.capture(
            distinct_id='test_user_1',
            event=event['event'],
            properties=event['properties']
        )
        
        print(f"✅ Evento enviado com response_time = {rt}s")
        time.sleep(1)  # Espera 1 segundo entre eventos
    
    print("\n🎉 Teste de response_time concluído!")

if __name__ == "__main__":
    test_response_time() 