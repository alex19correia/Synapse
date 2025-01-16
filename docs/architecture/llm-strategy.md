# Estratégia de LLMs 🤖

## Visão Geral
O Synapse utiliza uma abordagem multi-modelo para maximizar performance e confiabilidade, priorizando os melhores modelos disponíveis para uso pessoal.

## Modelos Principais

### GPT-4-Turbo (Primary)
- **Uso:** Raciocínio complexo e tarefas principais
- **Contexto:** 128k tokens
- **Custo:** ~$0.01/1K tokens
- **Casos de Uso:**
  - Planeamento estratégico
  - Análise profunda
  - Geração de conteúdo complexo
  - Tomada de decisão

### DeepSeek-33B (Secondary)
- **Uso:** Tarefas técnicas e código
- **Contexto:** 32k tokens
- **Custo:** Créditos disponíveis
- **Casos de Uso:**
  - Análise de código
  - Documentação técnica
  - Debugging
  - Otimização

### CodeLlama via Ollama (Local Fallback)
- **Uso:** Desenvolvimento e testes
- **Contexto:** 16k tokens
- **Custo:** Gratuito
- **Casos de Uso:**
  - Testes rápidos
  - Desenvolvimento offline
  - Tarefas locais

## Estratégia de Uso

### Seleção de Modelo
```python
def select_model(task_type: str, complexity: int) -> str:
    if task_type == "complex_reasoning" or complexity > 7:
        return "gpt-4-turbo"
    elif task_type == "technical" or task_type == "code":
        return "deepseek-33b"
    else:
        return "codellama"
```

### Fallback Strategy
1. Tentar GPT-4-Turbo
2. Se falhar, usar DeepSeek
3. Se offline, usar CodeLlama

## Monitorização e Otimização

### Métricas Chave
- Tempo de resposta
- Qualidade das respostas
- Custos por tipo de tarefa
- Taxa de sucesso/falha

### LangFuse Integration
```python
def log_llm_usage(model: str, tokens: int, success: bool):
    langfuse.log({
        "model": model,
        "tokens": tokens,
        "success": success,
        "timestamp": datetime.now()
    })
```

## Custos e Limites

### Limites Mensais
- GPT-4-Turbo: $50
- DeepSeek: Créditos disponíveis
- CodeLlama: Ilimitado (local)

### Otimização de Custos
1. Caching agressivo de respostas
2. Chunking eficiente de prompts
3. Reutilização de contexto

## Próximos Passos
1. Implementar sistema de cache
2. Adicionar mais métricas
3. Otimizar seleção de modelos
4. Explorar novos modelos promissores 