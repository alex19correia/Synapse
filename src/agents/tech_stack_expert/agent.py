from typing import Optional, Dict, List
from datetime import datetime
from src.core.base_agent import BaseAgent
from src.core.memory import ConversationMemory
from src.core.analytics import track_recommendation
from src.core.cache import Cache
from .models import TechStackRequirements, TechStackRecommendation

class TechStackExpertAgent(BaseAgent):
    """Agente especializado em recomendação de stacks tecnológicas com analytics e cache."""
    
    def __init__(
        self,
        memory: Optional[ConversationMemory] = None,
        cache: Optional[Cache] = None,
        analytics_enabled: bool = True
    ):
        super().__init__()
        self.memory = memory or ConversationMemory()
        self.cache = cache or Cache()
        self.analytics_enabled = analytics_enabled
        self.tech_knowledge_base = self._load_tech_knowledge_base()
    
    async def analyze_requirements(self, query: str, user_id: Optional[str] = None) -> str:
        """Analisa requisitos através de conversação guiada com contexto do usuário."""
        conversation_state = await self.memory.get_conversation_state(user_id)
        
        # Tenta recuperar do cache se for uma query similar
        cache_key = self._generate_cache_key(query, user_id)
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            return cached_response
            
        response = await self._process_conversation_step(conversation_state, query)
        
        # Cache a resposta para queries similares
        await self.cache.set(cache_key, response, expire=3600)  # 1 hora
        return response

    async def recommend_stack(self, requirements: TechStackRequirements, user_id: Optional[str] = None) -> TechStackRecommendation:
        """Gera recomendação personalizada com analytics."""
        # Verifica cache primeiro
        cache_key = f"stack_rec:{requirements.model_dump_json()}"
        cached_recommendation = await self.cache.get(cache_key)
        if cached_recommendation:
            return TechStackRecommendation.model_validate_json(cached_recommendation)

        # Gera nova recomendação
        recommendation = await self._generate_recommendation(requirements)
        
        # Registra analytics
        if self.analytics_enabled:
            await track_recommendation(
                user_id=user_id,
                requirements=requirements,
                recommendation=recommendation,
                timestamp=datetime.utcnow()
            )
        
        # Cache para futuras consultas similares
        await self.cache.set(cache_key, recommendation.model_dump_json(), expire=86400)  # 24 horas
        
        return recommendation

    def _load_tech_knowledge_base(self) -> Dict:
        """Carrega base de conhecimento tecnológico."""
        return {
            "frontend": {
                "simple": {
                    "primary": "Streamlit",
                    "conditions": ["low_traffic", "rapid_development"]
                },
                "complex": {
                    "primary": "Next.js",
                    "alternatives": ["React + Vite", "Svelte", "Vue"],
                    "conditions": ["high_traffic", "complex_ui"]
                }
            },
            "backend": {
                "ai_focused": {
                    "simple": "n8n/Flowise",
                    "complex": "LangChain + LangGraph"
                },
                "api": {
                    "python": "FastAPI",
                    "javascript": "Express",
                    "high_performance": "Go"
                }
            },
            "auth": {
                "default": "Supabase Auth",
                "enterprise": "Auth0",
                "conditions": {
                    "sso_required": "Auth0",
                    "simple_auth": "Supabase Auth"
                }
            },
            "database": {
                "default": {
                    "sql": "Supabase (PostgreSQL)",
                    "vector": "pgvector"
                },
                "specific": {
                    "nosql": ["MongoDB", "Firebase"],
                    "conditions": ["document_based", "real_time"]
                }
            },
            "llm": {
                "general": {
                    "primary": "Claude 3.5 Sonnet",
                    "cost_effective": "Claude 3.5 Haiku"
                },
                "private": {
                    "primary": "Ollama + Qwen",
                    "vision": "Llama 3.2"
                }
            }
        }

    async def _generate_recommendation(self, requirements: TechStackRequirements) -> TechStackRecommendation:
        """Gera recomendação baseada na base de conhecimento e requisitos."""
        kb = self.tech_knowledge_base
        
        # Lógica de seleção baseada em requisitos
        frontend = self._select_frontend(requirements, kb["frontend"])
        backend = self._select_backend(requirements, kb["backend"])
        auth = self._select_auth(requirements, kb["auth"])
        database = self._select_database(requirements, kb["database"])
        llm = self._select_llm(requirements, kb["llm"])
        
        reasoning = self._generate_reasoning(
            requirements,
            frontend,
            backend,
            auth,
            database,
            llm
        )
        
        return TechStackRecommendation(
            frontend=frontend,
            backend=backend,
            authentication=auth,
            database=database,
            llm=llm,
            reasoning=reasoning
        )

    def _select_frontend(self, requirements: TechStackRequirements, kb: Dict) -> Dict:
        """Seleciona tecnologias frontend baseado nos requisitos."""
        if requirements.ai_coding_assistant in ["Bolt.new", "Bolt.diy", "Lovable"]:
            return {"primary": "React + Vite", "reason": "Compatibilidade com AI coding assistant"}
            
        if requirements.user_scale in ["1-100", "100-1,000"] and "simple_ui" in requirements.specific_requirements:
            return kb["frontend"]["simple"]
            
        return kb["frontend"]["complex"]

    # Métodos similares para backend, auth, database e llm...

    def _generate_reasoning(self, requirements: TechStackRequirements, *selections) -> str:
        """Gera explicação detalhada das escolhas tecnológicas."""
        return f"""Baseado nos seus requisitos:
        
1. Frontend: {selections[0]['primary']}
   - Escolhido devido à {selections[0].get('reason', 'compatibilidade com suas necessidades')}
   
2. Backend: {selections[1]['primary']}
   - Otimizado para {requirements.user_scale} usuários
   
3. Autenticação: {selections[2]['primary']}
   - Adequado para suas necessidades de segurança
   
4. Banco de Dados: {selections[3]['primary']}
   - Escolhido considerando escalabilidade e requisitos de dados
   
5. LLM: {selections[4]['primary']}
   - Balanceando custo/benefício e suas necessidades específicas"""

    def _generate_cache_key(self, query: str, user_id: Optional[str]) -> str:
        """Gera chave de cache única para a query."""
        return f"tech_stack:{user_id}:{hash(query)}" 