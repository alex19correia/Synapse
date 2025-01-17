from posthog import Posthog
from datetime import datetime
import time

# Configuração do PostHog
posthog = Posthog(
    project_api_key='phc_FfrnE3gAla60Fcnj16QbpRtyNP3Nk5J92MJLUjZMaU9',
    host='https://eu.i.posthog.com'
)

def test_property_definition():
    """Força o registro da propriedade response_time"""
    
    # Define a propriedade primeiro
    event = {
        'event': '$set_property_definitions',
        'properties': {
            'response_time': {
                'type': 'numeric',
                'name': 'Response Time',
                'unit': 'seconds'
            }
        }
    }
    
    # Envia definição da propriedade
    posthog.capture(
        distinct_id='system',
        event=event['event'],
        properties=event['properties']
    )
    
    # Espera um pouco
    time.sleep(2)
    
    # Envia evento com a propriedade
    posthog.capture(
        distinct_id='test_user_1',
        event='llm_request',
        properties={
            'response_time': 1.5,
            '$set': {
                'response_time_enabled': True
            }
        }
    )
    
    print("✅ Propriedade definida e evento enviado!")

if __name__ == "__main__":
    test_property_definition() 