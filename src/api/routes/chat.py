"""Chat routes for the API."""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any

from src.api.dependencies import RAGDep, LLMDep
from src.schemas import ChatCompletionRequest, ChatCompletionResponse

router = APIRouter()

@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK
)
async def chat_completion(
    request: ChatCompletionRequest,
    rag_system: RAGDep,
    llm_client: LLMDep
) -> ChatCompletionResponse:
    """Chat completion endpoint.
    
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
            
            # Augment messages with context
            messages = request.messages[:-1]
            messages.append({
                "role": "system",
                "content": f"Use this context to answer the user's question:\n\n{rag_response['context']}"
            })
            messages.append(request.messages[-1])
            
            # Get completion from LLM
            llm_response = await llm_client.complete(messages, request.model)
            return ChatCompletionResponse(
                response=llm_response["response"],
                usage=llm_response["usage"]
            )
        else:
            # Use LLM directly
            llm_response = await llm_client.complete(request.messages, request.model)
            return ChatCompletionResponse(
                response=llm_response["response"],
                usage=llm_response["usage"]
            )
            
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

@router.post(
    "/chat/completions/stream",
    status_code=status.HTTP_200_OK
)
async def stream_completion(
    request: ChatCompletionRequest,
    llm_client: LLMDep
):
    """Stream chat completion endpoint.
    
    Args:
        request: Chat completion request
        llm_client: LLM client dependency
        
    Returns:
        Streaming chat completion response
        
    Raises:
        HTTPException: If streaming fails
    """
    async def generate():
        try:
            async for chunk in llm_client.stream(request.messages, request.model):
                yield str(chunk).encode() + b"\n"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Streaming failed: {str(e)}"
            )
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )