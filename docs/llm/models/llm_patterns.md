# Padrões de Interação LLM - Synapse

## 🎯 Objetivos
- Respostas consistentes
- Gestão eficiente de recursos
- Fallback robusto
- Tracking preciso

## 📝 Formatos de Prompt

### 1. Chat Básico
```python
{
    "role": "system",
    "content": "Você é o Synapse, um assistente pessoal focado em..."
}
{
    "role": "user",
    "content": "<mensagem do utilizador>"
}
```

### 2. RAG Enriched
```python
{
    "role": "system",
    "content": "Contexto: <dados recuperados>\n\nBaseado no contexto acima..."
}
```

## 🔄 Fluxo de Processamento

1. **Pré-processamento**
   - Validação de input
   - Enriquecimento contextual
   - Tokenização

2. **Processamento**
   - Seleção de modelo
   - Gestão de retry
   - Cache check

3. **Pós-processamento**
   - Validação de output
   - Formatação
   - Logging

## ⚡ Optimizações

### Cache
- TTL baseado em tipo de query
- Invalidação seletiva
- Cache em memória vs persistente

### Batch Processing
- Agregação de requests
- Processamento paralelo
- Queue management
