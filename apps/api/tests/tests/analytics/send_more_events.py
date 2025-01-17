from posthog import Posthog
from datetime import datetime, timedelta
import random

# Configuração do PostHog
posthog = Posthog(
    project_api_key='phc_FfrnE3gAla60Fcnj16QbpRtyNP3Nk5J92MJLUjZMaU9',
    host='https://eu.i.posthog.com'
)

def send_test_data():
    # Gerar dados para os últimos 7 dias
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        
        # Simular múltiplas mensagens por dia
        for _ in range(random.randint(3, 10)):
            posthog.capture(
                distinct_id=f"test_user_{random.randint(1,5)}", # 5 usuários diferentes
                event='message_sent',
                properties={
                    'message_type': random.choice(['query', 'response']),
                    'timestamp': date.isoformat(),
                    'environment': 'production'  # Importante: não é 'test'
                }
            )
    
    print("✅ Dados de teste enviados com sucesso!")

if __name__ == "__main__":
    send_test_data() 