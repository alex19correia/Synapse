import asyncio
import httpx
from loguru import logger

async def test_chat_endpoint():
    """Testa o endpoint de chat."""
    print("\n🔄 Iniciando teste do endpoint de chat...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Prepara a requisição
            url = "http://localhost:8000/sessions/test-session/messages"
            headers = {"Content-Type": "application/json"}
            data = {
                "content": "Olá, como vai?"
            }
            
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Data: {data}")
            logger.info(f"🔄 Enviando requisição POST para {url}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Dados: {data}")
            
            # Faz a requisição
            try:
                print("\n🔄 Enviando requisição...")
                response = await client.post(url, json=data, headers=headers)
                
                # Loga o resultado
                print(f"\nStatus: {response.status_code}")
                print(f"Response: {response.text}")
                logger.info(f"Status: {response.status_code}")
                logger.info(f"Response: {response.text}")
                
                if response.status_code != 200:
                    print(f"\n❌ Erro na resposta: {response.text}")
                    logger.error(f"Erro na resposta: {response.text}")
                else:
                    print("\n✅ Teste bem sucedido!")
                    logger.info("✅ Teste bem sucedido!")
                
                return response
                
            except httpx.RequestError as e:
                print(f"\n❌ Erro na requisição: {str(e)}")
                logger.error(f"❌ Erro na requisição: {str(e)}")
                raise
            
    except Exception as e:
        print(f"\n❌ Erro ao testar endpoint: {str(e)}")
        logger.error(f"❌ Erro ao testar endpoint: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        print("\n🚀 Iniciando teste...")
        asyncio.run(test_chat_endpoint())
        print("\n✨ Teste finalizado!")
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        logger.info("Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro não tratado: {str(e)}")
        logger.error(f"Erro não tratado: {str(e)}")
        raise 