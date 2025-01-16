"""Exemplo de uso do DeepSeek."""
import asyncio
from src.llm.deepseek_client import DeepSeekClient, DeepSeekMessage

async def main():
    """Função principal."""
    client = DeepSeekClient()
    
    # Exemplo de geração simples
    messages = [
        DeepSeekMessage(
            role="system",
            content="Você é um assistente útil e amigável."
        ),
        DeepSeekMessage(
            role="user",
            content="Olá! Como você está?"
        )
    ]
    
    print("\n=== Geração Simples ===")
    response = await client.generate_with_cache(messages)
    print(f"Resposta: {response.content}")
    print(f"Tokens: {response.usage}")
    
    # Exemplo de streaming
    print("\n=== Streaming ===")
    print("Resposta: ", end="", flush=True)
    async for token in client.stream_generate(messages):
        print(token, end="", flush=True)
    print("\n")
    
    # Exemplo de resumo
    text = """
    Python é uma linguagem de programação de alto nível, interpretada, 
    de script, imperativa, orientada a objetos, funcional, de tipagem dinâmica e forte.
    Foi lançada por Guido van Rossum em 1991. Possui uma filosofia de design que 
    enfatiza a legibilidade do código com o uso de indentação significativa.
    O Python é uma linguagem que suporta múltiplos paradigmas de programação, 
    incluindo programação procedural, orientada a objetos e funcional.
    """
    
    print("\n=== Resumo ===")
    summary = await client.summarize(text, max_length=100)
    print(f"Resumo: {summary}")
    
    # Exemplo de extração de entidades
    print("\n=== Extração de Entidades ===")
    entities = await client.extract_entities(text)
    print("Entidades encontradas:")
    for entity in entities:
        print(f"- {entity.text} ({entity.type})")

if __name__ == "__main__":
    asyncio.run(main()) 