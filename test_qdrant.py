import requests

def test_qdrant_connection():
    try:
        response = requests.get("http://localhost:6335/readyz")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    if test_qdrant_connection():
        print("✅ Conexão com Qdrant bem-sucedida!")
    else:
        print("❌ Falha na conexão com Qdrant") 