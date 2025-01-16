from posthog import Posthog

class AnalyticsService:
    def __init__(self):
        self.client = Posthog(
            project_api_key='phc_FfrnE3gAla60Fcnj16QbpRtyNP3Nk5J92MJLUjZMaU9',
            host='https://eu.i.posthog.com'
        )
    
    def track(self, event: str, properties: dict = None):
        try:
            self.client.capture(
                distinct_id='cli_user',
                event=event,
                properties=properties or {}
            )
        except Exception as e:
            print(f"Erro ao registrar evento: {e}") 