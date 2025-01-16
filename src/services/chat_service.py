from typing import Optional
from loguru import logger
from fastapi import HTTPException

from .message_service import MessageService
from .llm_service import LLMService
from ..models.message import Message

class ChatService:
    """Serviço para gerenciar o chat."""
    
    def __init__(self, message_service: MessageService, llm_service: LLMService):
        self.message_service = message_service
        self.llm_service = llm_service
        logger.debug(f"🔧 ChatService inicializado com: {message_service=}, {llm_service=}")
        
    async def process_message(self, session_id: str, content: str) -> Message:
        """
        Processa uma mensagem do usuário e retorna a resposta.
        
        Args:
            session_id: ID da sessão do chat
            content: Conteúdo da mensagem
            
        Returns:
            Message: Mensagem de resposta do assistente
            
        Raises:
            HTTPException: Se ocorrer algum erro no processamento
        """
        try:
            # Validações básicas
            if not session_id:
                raise ValueError("ID da sessão não pode estar vazio")
            if not content:
                raise ValueError("Conteúdo da mensagem não pode estar vazio")
                
            logger.debug(f"📨 Processando mensagem para sessão {session_id}")
            logger.debug(f"📝 Conteúdo: {content}")
            
            # Salva mensagem do usuário
            logger.debug("💾 Salvando mensagem do usuário...")
            user_message = await self.message_service.save_message(
                session_id=session_id,
                role="user",
                content=content
            )
            logger.debug(f"✅ Mensagem do usuário salva: {user_message}")
            
            # Obtém histórico da conversa
            logger.debug("📚 Obtendo histórico da conversa...")
            messages = await self.message_service.get_session_messages(session_id)
            logger.debug(f"✅ Histórico obtido: {len(messages)} mensagens")
            
            # Gera resposta do assistente
            logger.debug("🤖 Gerando resposta do assistente...")
            response = await self.llm_service.get_completion(
                prompt=content,
                context={"messages": messages}
            )
            
            if not response:
                raise ValueError("LLM retornou uma resposta vazia")
                
            logger.debug(f"✅ Resposta gerada: {response}")
            
            # Salva e retorna resposta
            logger.debug("💾 Salvando resposta do assistente...")
            assistant_message = await self.message_service.save_message(
                session_id=session_id,
                role="assistant", 
                content=response
            )
            logger.debug(f"✅ Resposta salva: {assistant_message}")
            
            return assistant_message
            
        except ValueError as e:
            logger.error(f"❌ Erro de validação: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {str(e)}")
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao processar mensagem"
            ) 