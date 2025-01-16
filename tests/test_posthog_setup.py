from posthog import Posthog
import os

def test_posthog_connection():
    # Configurar PostHog
    posthog = Posthog(
        project_api_key='phc_FfrnE3gA1aG8Fcnj16QbpRtyNP',  # sua API key
        host='https://app.posthog.com'
    )
    
    # Enviar evento de teste
    posthog.capture(
        'test-id',
        'test-event',
        {
            'property1': 'value1',
            'property2': 'value2'
        }
    )
    
    print("✅ Evento enviado com sucesso!")

if __name__ == "__main__":
    test_posthog_connection() 