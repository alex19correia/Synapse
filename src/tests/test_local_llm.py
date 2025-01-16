import asyncio
from src.config.llm_config import LLMConfig
from src.core.cache import CacheService
from src.services.llm_service import LLMService

async def test_codellama():
    """Testa o modelo CodeLlama local"""
    
    # Configuração básica
    config = LLMConfig(
        temperature=0.2,  # Baixa temperatura para respostas mais consistentes
        max_tokens=2000
    )
    
    # Inicializar serviços
    cache = CacheService()  # Mock do cache para teste
    llm = LLMService(cache, config)
    
    # Testar com algumas perguntas
    prompts = [
        "Explica como funciona o CodeLlama em 3 pontos.",
        "Qual a diferença entre uma lista e um dicionário em Python?",
        "Como implementar um decorator em Python? Dá um exemplo simples."
    ]
    
    for prompt in prompts:
        print(f"\n🤖 Testando prompt: {prompt}\n")
        try:
            response = await llm.test_local_model(prompt)
            print(f"✅ Resposta:\n{response}\n")
        except Exception as e:
            print(f"❌ Erro: {str(e)}\n")
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(test_codellama()) 