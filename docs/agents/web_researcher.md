# Web Researcher Agent 🔍

## Descrição
Agente especializado em pesquisa web usando a API do Brave Search e LLMs para fornecer respostas contextualizadas.

## Funcionalidades

### 1. Pesquisa Web
- Busca em tempo real via Brave Search API
- Processamento de resultados com LLM
- Suporte a múltiplos idiomas

### 2. Configuração
```python
config = {
    "brave_api_key": "sua_chave_api",
    "max_results": 3,
    "search_lang": "en"
}
```

### 3. Exemplos de Uso
```python
# Via API
POST /web-researcher/search
{
    "query": "Latest developments in AI"
}

# Via código
agent = WebResearcherAgent()
result = await agent.search_web("Latest developments in AI")
```

## Testes
```bash
# Executar testes do agente
pytest tests/agents/web_researcher/test_agent.py -v
```

## Dependências
- Brave Search API
- OpenAI API ou Ollama
- HTTPX para requisições assíncronas 