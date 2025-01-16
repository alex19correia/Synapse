"""Chat completion endpoint."""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from src.api.dependencies import RAGDep, LLMDep
from src.schemas import ChatCompletionRequest, ChatCompletionResponse

router = APIRouter()

@router.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK
)
async def chat_completion(
    request: ChatCompletionRequest,
    rag_system: RAGDep,
    llm_client: LLMDep
) -> ChatCompletionResponse:
    """
    Chat completion endpoint.
    
    Args:
        request: Chat completion request
        rag_system: RAG system dependency
        llm_client: LLM client dependency
        
    Returns:
        Chat completion response
        
    Raises:
        HTTPException: If completion fails
    """
    try:
        if request.use_rag:
            if not request.messages:
                raise ValueError("No messages provided")
                
            # Use RAG system
            last_message = request.messages[-1].content
            rag_response = await rag_system.query(last_message)
            
            # Calculate token usage
            prompt_tokens = len(last_message.split())
            completion_tokens = len(rag_response["response"].split())
            
            return ChatCompletionResponse(
                response=rag_response["response"],
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            )
        else:
            # Use LLM directly
            return llm_client.complete(request.messages, request.model)
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}"
        ) 