from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncGenerator, Optional

import logfire
from httpx import AsyncClient, HTTPError
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI
from src.cache.redis_cache import RedisCache
from src.analytics.analytics_service import AnalyticsService

# Nova configuração do Logfire
logfire.configure(
    send_to_logfire='if-token-present',
    environment=os.getenv('ENVIRONMENT', 'development'),
    service_name='web-researcher-agent'
)

@dataclass
class WebResearcherDeps:
    client: AsyncClient
    brave_api_key: str | None
    cache: Optional[RedisCache] = None
    analytics: Optional[AnalyticsService] = None

class WebResearcherAgent:
    def __init__(self, use_cache: bool = False):
        openai_client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        model_name = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        model = OpenAIModel(model_name, openai_client=openai_client)
        
        self.agent = Agent(
            model,
            system_prompt=self._get_system_prompt(),
            deps_type=WebResearcherDeps,
            retries=2
        )
        
        self.cache = RedisCache() if use_cache else None

    def _get_system_prompt(self) -> str:
        return f"""You are an expert at researching the web to answer user questions.
        Current date: {datetime.now().strftime("%Y-%m-%d")}
        
        Guidelines:
        1. Always cite sources when providing information
        2. Indicate confidence level in the information
        3. Highlight any conflicting information found
        4. Use bullet points for clarity when appropriate
        """

    async def _search_brave(
        self, 
        client: AsyncClient, 
        query: str, 
        api_key: str,
        max_results: int = 3
    ) -> str:
        """Executa busca usando Brave Search API."""
        headers = {
            'X-Subscription-Token': api_key,
            'Accept': 'application/json',
        }
        
        try:
            r = await client.get(
                'https://api.search.brave.com/res/v1/web/search',
                params={
                    'q': query,
                    'count': max_results * 2,
                    'text_decorations': True,
                    'search_lang': 'en'
                },
                headers=headers,
                timeout=10.0
            )
            await r.aread()  # Garante que a resposta é lida completamente
            await r.raise_for_status()
            data = r.json()

            results = []
            web_results = data.get('web', {}).get('results', [])
            
            for item in web_results[:max_results]:
                title = item.get('title', '')
                description = item.get('description', '')
                url = item.get('url', '')
                if title and description:
                    results.append(f"Title: {title}\nSummary: {description}\nSource: {url}\n")

            return "\n".join(results) if results else "No results found for the query."
            
        except Exception as e:
            logfire.error("brave_search_error", error=str(e))
            raise

    async def search_web(
        self, 
        query: str, 
        brave_api_key: str | None = None,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """Realiza pesquisa web."""
        if brave_api_key is None:
            return "This is a test web search result. Please provide a Brave API key to get real search results."

        async with AsyncClient() as client:
            try:
                search_results = await self._search_brave(client, query, brave_api_key)
                
                if stream:
                    return self.agent.run_stream(
                        f"Based on these search results, answer the query: {query}\n\nSearch Results:\n{search_results}",
                        deps=WebResearcherDeps(client=client, brave_api_key=brave_api_key)
                    )
                else:
                    result = await self.agent.run(
                        f"Based on these search results, answer the query: {query}\n\nSearch Results:\n{search_results}",
                        deps=WebResearcherDeps(client=client, brave_api_key=brave_api_key)
                    )
                    return result.data
                    
            except Exception as e:
                error_msg = f"Error processing query: {str(e)}"
                logfire.error("web_researcher_error", error=str(e), query=query)
                return error_msg 