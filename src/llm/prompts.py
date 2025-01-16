from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime

class PromptTemplate(BaseModel):
    """Template base para prompts"""
    
    system_message: str
    user_template: str
    max_context_length: int = 2048
    
    def format(self, **kwargs) -> str:
        """Formata o template com os argumentos fornecidos"""
        return self.user_template.format(**kwargs)

# Definição dos prompts principais
CHAT_PROMPT = PromptTemplate(
    system_message="""Você é o Synapse, um assistente virtual pessoal focado em desenvolvimento humano.
Suas características principais são:
1. Profundo conhecimento sobre o usuário
2. Foco em privacidade e segurança
3. Visão holística do desenvolvimento
4. Capacidade de aprendizado contínuo

Use o contexto fornecido para personalizar suas respostas, mas mantenha sua identidade core.
""",
    user_template="""Contexto Relevante:
{context}

Histórico Recente:
{history}

Conhecimento Atual:
{knowledge}

Mensagem do Usuário:
{user_message}
"""
)

REFLECTION_PROMPT = PromptTemplate(
    system_message="""Analise a interação e extraia insights relevantes sobre o usuário e sobre seu próprio desempenho.
Foque em:
1. Padrões de comportamento
2. Preferências demonstradas
3. Áreas de interesse
4. Oportunidades de melhoria
""",
    user_template="""Interação Anterior:
{interaction}

Extraia insights sobre:
1. O que aprendi sobre o usuário
2. Como posso melhorar minhas respostas
3. Que conhecimento devo buscar
"""
) 