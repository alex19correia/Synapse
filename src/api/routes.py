from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime

from ..models.chat import ChatRequest, ChatResponse
from ..models.user import User, UserCreate, UserPreferences

# Routers
api_router = APIRouter()
auth_router = APIRouter(prefix="/auth", tags=["auth"])
chat_router = APIRouter(prefix="/chat", tags=["chat"])
user_router = APIRouter(prefix="/users", tags=["users"])

# Rotas de autenticação
@auth_router.post("/verify")
async def verify_token():
    """Verifica se o token de autenticação é válido."""
    # TODO: Implementar verificação com Clerk
    return {"valid": True}

# Rotas de chat
@chat_router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Envia uma mensagem para o assistente."""
    try:
        # TODO: Implementar integração com LLM
        return ChatResponse(
            response="Olá! Ainda estou em desenvolvimento, mas em breve poderei ajudar-te! 😊",
            session_id=request.session_id or "new_session",
            provider="development",
            model="test"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rotas de utilizador
@user_router.post("/", response_model=User)
async def create_user(user: UserCreate):
    """Cria um novo utilizador."""
    # TODO: Implementar criação de utilizador
    pass

@user_router.get("/me", response_model=User)
async def get_current_user():
    """Obtém o utilizador atual."""
    # TODO: Implementar obtenção do utilizador atual
    pass

# Registrar os routers
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(user_router) 