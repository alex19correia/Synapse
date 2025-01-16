import asyncio
import json
import uuid
import httpx
from datetime import datetime, timezone

async def test_chat():
    try:
        session_id = str(uuid.uuid4())
        message = "Olá! Como estás?"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://127.0.0.1:8000/chat/sessions/{session_id}/messages",
                json={"content": message}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Teste concluído com sucesso!")
                print(f"Mensagem enviada: {message}")
                print(f"Resposta: {data.get('content')}")
            else:
                print(f"\n❌ Erro: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_chat()) 