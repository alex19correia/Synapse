cache_config = {
    "provider": "redis",
    "ttl": {
        "embeddings": 3600,  # 1 hora
        "chat_responses": 1800,  # 30 minutos
        "user_context": 7200  # 2 horas
    },
    "fallback": {
        "enabled": True,
        "models": ["gpt-3.5-turbo", "llama-2-13b"]
    }
} 