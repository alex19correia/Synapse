import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Testa o endpoint raiz da API."""
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_health_check():
    """Testa o endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_chat_session():
    """Testa a criação de uma sessão de chat."""
    response = client.post(
        "/chat/sessions",
        json={"user_id": "test-user", "title": "Test Session"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Session"

@pytest.mark.asyncio
async def test_add_message():
    """Testa a adição de uma mensagem ao chat."""
    # Primeiro cria uma sessão
    session_response = client.post(
        "/chat/sessions",
        json={"user_id": "test-user", "title": "Test Session"}
    )
    session_id = session_response.json()["id"]
    
    # Adiciona uma mensagem
    response = client.post(
        "/chat/messages",
        json={
            "session_id": session_id,
            "role": "user",
            "content": "Test message"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Test message" 