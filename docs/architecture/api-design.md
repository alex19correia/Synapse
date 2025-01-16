# API Design & Architecture 🌐

## Visão Geral
O Synapse utiliza FastAPI para expor uma API RESTful moderna, com suporte a WebSockets para comunicação em tempo real.

## Estrutura Base

### 1. Endpoints Principais
```python
api_structure = {
    "auth": {
        "POST /auth/login": "Login do utilizador",
        "POST /auth/refresh": "Refresh do token",
        "POST /auth/logout": "Logout do utilizador"
    },
    "chat": {
        "POST /chat/message": "Enviar mensagem",
        "GET /chat/history": "Obter histórico",
        "WS /chat/stream": "Stream de chat"
    },
    "tasks": {
        "GET /tasks": "Listar tarefas",
        "POST /tasks": "Criar tarefa",
        "PUT /tasks/{id}": "Atualizar tarefa",
        "DELETE /tasks/{id}": "Remover tarefa"
    },
    "plugins": {
        "GET /plugins": "Listar plugins",
        "POST /plugins/{id}/execute": "Executar plugin"
    }
}
```

### 2. Modelos de Dados

#### 2.1 Base Models
```python
from pydantic import BaseModel

class Message(BaseModel):
    """Modelo de mensagem."""
    id: str
    content: str
    role: str
    timestamp: datetime
    metadata: Dict[str, Any]

class Task(BaseModel):
    """Modelo de tarefa."""
    id: str
    title: str
    description: str
    due_date: Optional[datetime]
    status: TaskStatus
    priority: Priority
```

### 3. Middleware Stack

#### 3.1 Security
```python
security_layers = {
    "authentication": {
        "JWT": "JSON Web Tokens",
        "API Keys": "Para integrações",
        "OAuth2": "Social logins"
    },
    "rate_limiting": {
        "global": "100 req/min",
        "user": "20 req/min",
        "ip": "50 req/min"
    }
}
```

#### 3.2 Performance
```python
performance_config = {
    "caching": {
        "strategy": "Redis",
        "ttl": {
            "short": "5min",
            "medium": "1h",
            "long": "24h"
        }
    },
    "compression": "gzip",
    "pagination": {
        "default_size": 20,
        "max_size": 100
    }
}
```

### 4. WebSocket Integration

#### 4.1 Chat Stream
```python
websocket_routes = {
    "/ws/chat": {
        "events": [
            "message.new",
            "message.update",
            "typing.start",
            "typing.stop"
        ],
        "features": [
            "Auto-reconnect",
            "Heartbeat",
            "Message queue"
        ]
    }
}
```

### 5. Error Handling

#### 5.1 HTTP Errors
```python
error_responses = {
    "400": {
        "description": "Bad Request",
        "schema": {"error": "Detalhes do erro"}
    },
    "401": {
        "description": "Unauthorized",
        "schema": {"error": "Credenciais inválidas"}
    },
    "403": {
        "description": "Forbidden",
        "schema": {"error": "Sem permissões"}
    },
    "404": {
        "description": "Not Found",
        "schema": {"error": "Recurso não encontrado"}
    },
    "429": {
        "description": "Too Many Requests",
        "schema": {"error": "Rate limit excedido"}
    }
}
```

### 6. Documentação

#### 6.1 OpenAPI Spec
```python
openapi_config = {
    "title": "Synapse API",
    "description": "API do assistente pessoal Synapse",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc"
}
```

### 7. Exemplos de Uso

#### 7.1 Chat Message
```python
@router.post("/chat/message")
async def send_message(
    message: Message,
    current_user: User = Depends(get_current_user)
) -> MessageResponse:
    """Envia uma mensagem para o Synapse.
    
    Args:
        message: Conteúdo da mensagem
        current_user: Utilizador atual
        
    Returns:
        MessageResponse com a resposta do Synapse
    """
```

### 8. Monitorização

#### 8.1 Métricas
```python
monitoring_setup = {
    "metrics": [
        "Request duration",
        "Error rates",
        "Active users",
        "API usage"
    ],
    "logging": {
        "request_id": True,
        "user_id": True,
        "ip_address": True,
        "timestamp": True
    }
}
```

### 9. Próximos Passos
1. Implementar rate limiting
2. Adicionar mais endpoints
3. Melhorar documentação
4. Implementar testes E2E
5. Setup monitoring

## Referências
- [FastAPI Best Practices](https://fastapi.tiangolo.com/advanced/best-practices/)
- [REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [WebSocket Best Practices](https://websockets.readthedocs.io/en/stable/intro.html) 



