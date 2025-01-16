# API Documentation 🌐

## Visão Geral
A API do Synapse segue os princípios REST e utiliza JSON para comunicação. Todos os endpoints requerem autenticação via Bearer token.

## Base URL
```
https://api.synapse.ai/v1
```

## Autenticação

### 1. Endpoints de Auth
```python
auth_endpoints = {
    "POST /auth/login": {
        "descrição": "Autenticar utilizador",
        "body": {
            "email": "string",
            "password": "string"
        },
        "response": {
            "access_token": "string",
            "refresh_token": "string",
            "token_type": "Bearer"
        }
    },
    "POST /auth/refresh": {
        "descrição": "Renovar token",
        "body": {
            "refresh_token": "string"
        },
        "response": {
            "access_token": "string"
        }
    }
}
```

## Chat API

### 1. Mensagens
```python
chat_endpoints = {
    "POST /chat/message": {
        "descrição": "Enviar mensagem",
        "body": {
            "content": "string",
            "context": "optional dict"
        },
        "response": {
            "message_id": "string",
            "response": "string",
            "tokens_used": "int"
        }
    },
    "GET /chat/history": {
        "descrição": "Obter histórico",
        "params": {
            "limit": "int, default=50",
            "before": "timestamp, optional"
        },
        "response": {
            "messages": "List[Message]",
            "has_more": "boolean"
        }
    }
}
```

### 2. Streaming
```python
streaming_endpoints = {
    "WS /chat/stream": {
        "descrição": "Stream de chat",
        "protocol": "WebSocket",
        "messages": {
            "user": {
                "type": "message",
                "content": "string"
            },
            "assistant": {
                "type": "token",
                "content": "string"
            }
        }
    }
}
```

## Tasks API

### 1. Gestão de Tarefas
```python
task_endpoints = {
    "GET /tasks": {
        "descrição": "Listar tarefas",
        "params": {
            "status": "enum[pending,done]",
            "priority": "enum[low,medium,high]"
        },
        "response": {
            "tasks": "List[Task]",
            "total": "int"
        }
    },
    "POST /tasks": {
        "descrição": "Criar tarefa",
        "body": {
            "title": "string",
            "description": "string",
            "due_date": "datetime",
            "priority": "enum"
        },
        "response": "Task"
    }
}
```

## Plugin API

### 1. Gestão de Plugins
```python
plugin_endpoints = {
    "GET /plugins": {
        "descrição": "Listar plugins",
        "response": {
            "plugins": "List[Plugin]",
            "total": "int"
        }
    },
    "POST /plugins/{id}/execute": {
        "descrição": "Executar plugin",
        "params": {
            "id": "string"
        },
        "body": {
            "action": "string",
            "params": "dict"
        },
        "response": {
            "result": "Any",
            "status": "string"
        }
    }
}
```

## User API

### 1. Perfil e Preferências
```python
user_endpoints = {
    "GET /user/profile": {
        "descrição": "Obter perfil",
        "response": {
            "id": "string",
            "name": "string",
            "email": "string",
            "preferences": "dict"
        }
    },
    "PATCH /user/preferences": {
        "descrição": "Atualizar preferências",
        "body": {
            "key": "value"
        },
        "response": {
            "preferences": "dict"
        }
    }
}
```

## Responses

### 1. Formato Padrão
```python
response_format = {
    "success": {
        "status": 200,
        "data": "payload",
        "meta": {
            "timestamp": "ISO datetime",
            "request_id": "string"
        }
    },
    "error": {
        "status": "4xx/5xx",
        "error": {
            "code": "string",
            "message": "string",
            "details": "optional"
        },
        "meta": {
            "timestamp": "ISO datetime",
            "request_id": "string"
        }
    }
}
```

### 2. Códigos de Erro
```python
error_codes = {
    "400": "Bad Request",
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "Not Found",
    "429": "Too Many Requests",
    "500": "Internal Server Error"
}
```

## Rate Limiting

### 1. Limites
```python
rate_limits = {
    "default": {
        "rate": "100/min",
        "burst": "150"
    },
    "chat": {
        "rate": "20/min",
        "burst": "30"
    },
    "plugins": {
        "rate": "50/min",
        "burst": "75"
    }
}
```

## Próximos Passos
1. Implementar versionamento
2. Adicionar mais exemplos
3. Melhorar documentação
4. Adicionar Swagger UI
5. Criar postman collection

## Referências
- [REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/) 