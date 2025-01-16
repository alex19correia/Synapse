# WebSocket System Architecture 🔌

## Visão Geral
O sistema de WebSocket do Synapse fornece comunicação bidirecional em tempo real, otimizada para chat e atualizações ao vivo.

## Arquitetura

### 1. Conexões

#### 1.1 Setup
```python
websocket_config = {
    "server": {
        "engine": "FastAPI + WebSockets",
        "protocol": "wss://",
        "heartbeat": {
            "interval": "30s",
            "timeout": "90s"
        }
    },
    "scaling": {
        "type": "Redis PubSub",
        "channels": {
            "broadcast": "all clients",
            "user": "user specific",
            "room": "chat rooms"
        }
    }
}
```

### 2. Gestão de Conexões

#### 2.1 Connection Manager
```python
connection_manager = {
    "features": {
        "tracking": {
            "active_connections": "Set[WebSocket]",
            "user_sessions": "Dict[str, Set[WebSocket]]",
            "room_members": "Dict[str, Set[WebSocket]]"
        },
        "operations": {
            "connect": "Register new connection",
            "disconnect": "Clean up resources",
            "heartbeat": "Keep-alive check"
        }
    },
    "example": """
        class ConnectionManager:
            def __init__(self):
                self.active_connections = set()
                self.user_sessions = defaultdict(set)
                
            async def connect(self, websocket: WebSocket, user_id: str):
                await websocket.accept()
                self.active_connections.add(websocket)
                self.user_sessions[user_id].add(websocket)
                
            async def disconnect(self, websocket: WebSocket, user_id: str):
                self.active_connections.remove(websocket)
                self.user_sessions[user_id].remove(websocket)
    """
}
```

### 3. Mensagens

#### 3.1 Message Protocol
```python
message_protocol = {
    "formats": {
        "text": {
            "type": "chat",
            "content": "string",
            "timestamp": "ISO datetime"
        },
        "system": {
            "type": "notification",
            "action": "string",
            "data": "any"
        },
        "control": {
            "type": "heartbeat",
            "status": "string"
        }
    },
    "validation": {
        "size": "Max 64KB",
        "rate": "Max 60/minute",
        "format": "JSON"
    }
}
```

### 4. Rooms

#### 4.1 Chat Rooms
```python
chat_rooms = {
    "structure": {
        "room": {
            "id": "UUID",
            "type": "public|private",
            "members": "Set[str]",
            "metadata": "Dict"
        }
    },
    "operations": {
        "join": "Add user to room",
        "leave": "Remove from room",
        "message": "Broadcast to room"
    },
    "persistence": {
        "messages": "PostgreSQL",
        "state": "Redis",
        "ttl": "24h inactive"
    }
}
```

### 5. Escalabilidade

#### 5.1 Redis PubSub
```python
pubsub_system = {
    "channels": {
        "naming": {
            "broadcast": "broadcast",
            "user": "user:{user_id}",
            "room": "room:{room_id}"
        },
        "patterns": {
            "user_events": "user:*",
            "room_events": "room:*"
        }
    },
    "messages": {
        "structure": {
            "channel": "string",
            "message": "JSON string",
            "timestamp": "int"
        },
        "types": [
            "chat_message",
            "user_event",
            "system_event"
        ]
    }
}
```

### 6. Segurança

#### 6.1 Security Measures
```python
security = {
    "authentication": {
        "initial": "JWT validation",
        "ongoing": "Session check"
    },
    "rate_limiting": {
        "connection": "5 per second",
        "messages": "60 per minute"
    },
    "validation": {
        "origin": "Whitelist check",
        "payload": "Size and content",
        "protocol": "WebSocket only"
    }
}
```

### 7. Monitorização

#### 7.1 Metrics
```python
monitoring = {
    "metrics": {
        "connections": [
            "Active connections",
            "Connection rate",
            "Disconnect rate"
        ],
        "messages": [
            "Messages per second",
            "Message size",
            "Error rate"
        ],
        "latency": [
            "Connection time",
            "Message delivery",
            "Round trip time"
        ]
    },
    "alerts": {
        "high_load": "> 1000 connections",
        "error_rate": "> 1% messages",
        "latency": "> 100ms RTT"
    }
}
```

### 8. Error Handling

#### 8.1 Recovery Strategies
```python
error_handling = {
    "connection_lost": {
        "detection": "Heartbeat timeout",
        "action": "Auto-reconnect",
        "backoff": "Exponential"
    },
    "message_failed": {
        "retry": {
            "attempts": 3,
            "delay": "1s exponential"
        },
        "fallback": "REST API"
    },
    "server_error": {
        "circuit_breaker": {
            "threshold": "50% errors",
            "timeout": "30s"
        }
    }
}
```

## Próximos Passos
1. Implementar heartbeat
2. Setup monitoring
3. Otimizar scaling
4. Documentar protocols
5. Testes de carga

## Referências
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Redis PubSub](https://redis.io/topics/pubsub)
- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455) 