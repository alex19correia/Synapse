import os
import asyncio
from httpx import AsyncClient
from dotenv import load_dotenv

load_dotenv()

async def test_brave_search():
    brave_api_key = os.getenv('BRAVE_API_KEY')
    if not brave_api_key:
        print("❌ BRAVE_API_KEY não encontrada no .env")
        return

    print(f"🔑 Usando BRAVE_API_KEY: {brave_api_key[:4]}...{brave_api_key[-4:]}")

    headers = {
        'X-Subscription-Token': brave_api_key,
        'Accept': 'application/json',
    }

    async with AsyncClient() as client:
        try:
            r = await client.get(
                'https://api.search.brave.com/res/v1/web/search',
                params={
                    'q': 'Python programming',
                    'count': 3,
                    'text_decorations': True,
                    'search_lang': 'en'
                },
                headers=headers
            )
            r.raise_for_status()
            data = r.json()
            
            print("\n✅ API do Brave funcionando!")
            print("\nResultados:")
            for item in data.get('web', {}).get('results', []):
                print(f"\n📄 Título: {item.get('title')}")
                print(f"🔗 URL: {item.get('url')}")
                print(f"📝 Descrição: {item.get('description')}")
                
        except Exception as e:
            print(f"\n❌ Erro ao chamar API do Brave: {str(e)}")
            if hasattr(r, 'text'):
                print(f"\nResposta da API: {r.text}")

if __name__ == "__main__":
    asyncio.run(test_brave_search()) 