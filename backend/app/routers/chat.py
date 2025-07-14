"""
채팅 관련 API 라우터
확장된 채팅 기능을 위한 엔드포인트들
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any
import json
import asyncio
from loguru import logger

# 모델 및 서비스 임포트
from ..models import (
    ChatRequest, ChatResponseChunk, AvailableModelsResponse, 
    ModelInfo, ErrorResponse, SuccessResponse
)
from ..services.llm_service import llm_service
from ..services.prompt_processor import PromptProcessor

router = APIRouter(prefix="/api", tags=["chat"])

@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    """
    사용 가능한 모델 목록을 반환합니다.
    """
    try:
        supported_models = llm_service.get_supported_models()
        
        # ModelInfo 형태로 변환
        models_info = {}
        for model_name, model_data in supported_models.items():
            models_info[model_name] = ModelInfo(
                name=model_name,
                provider=model_data["provider"],
                max_tokens=model_data["max_tokens"],
                temperature_range=model_data["temperature_range"],
                description=model_data["description"]
            )
        
        return AvailableModelsResponse(
            models=models_info,
            total_count=len(models_info)
        )
        
    except Exception as e:
        logger.error(f"모델 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"모델 목록 조회 실패: {str(e)}"
        )

@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    """
    확장된 채팅 스트리밍 엔드포인트
    변수 치환, 시스템 프롬프트, 고급 파라미터를 지원합니다.
    """
    try:
        # 디버깅: 요청 데이터 로깅
        logger.info(f"채팅 요청 수신: {len(request.messages)}개 메시지, 모델: {request.settings.model}")
        logger.debug(f"요청 상세: {request.model_dump_json()}")
        # 1. 변수 치환 처리
        if request.variables:
            logger.info(f"변수 치환 시작: {len(request.variables)}개 변수")
            
            # 메시지들을 딕셔너리 형태로 변환
            messages_dict = [
                {"role": msg.role.value, "content": msg.content}
                for msg in request.messages
            ]
            
            # 변수 치환 적용
            processed_messages = PromptProcessor.process_messages_with_variables(
                messages_dict, 
                request.variables
            )
            
            # 다시 ChatMessage 형태로 변환
            processed_chat_messages = []
            for i, msg_dict in enumerate(processed_messages):
                msg = request.messages[i]
                msg.content = msg_dict["content"]
                processed_chat_messages.append(msg)
            
            request.messages = processed_chat_messages
            
            logger.info("변수 치환 완료")
        
        # 2. 메시지 검증
        if not request.messages:
            raise HTTPException(
                status_code=400, 
                detail="최소 하나의 메시지가 필요합니다."
            )
        
        # 3. 모델 설정 검증
        settings = request.settings
        if not llm_service.validate_model(settings.model):
            raise HTTPException(
                status_code=400, 
                detail=f"지원되지 않는 모델: {settings.model}"
            )
        
        # 4. 스트리밍 응답 생성
        async def generate_response() -> AsyncGenerator[str, None]:
            try:
                # 메시지를 딕셔너리 형태로 변환 (LLM 서비스 호환)
                messages_dict = [
                    {"role": msg.role.value, "content": msg.content}
                    for msg in request.messages
                ]
                
                # 실제 LLM 서비스 호출
                async for chunk_content in llm_service.generate_response(
                    messages=messages_dict,
                    model_name=settings.model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    system_prompt=request.system_prompt
                ):
                    response_chunk = ChatResponseChunk(
                        content=chunk_content,
                        is_complete=False,
                        model=settings.model
                    )
                    
                    yield f"data: {response_chunk.model_dump_json()}\n\n"
                
                # 완료 청크 전송
                final_chunk = ChatResponseChunk(
                    content="",
                    is_complete=True,
                    model=settings.model
                )
                yield f"data: {final_chunk.model_dump_json()}\n\n"
                
                logger.info(f"채팅 스트리밍 완료: 모델 {settings.model}")
                
            except Exception as e:
                logger.error(f"스트리밍 응답 생성 중 오류: {str(e)}")
                error_response = ChatResponseChunk(
                    content=f"오류가 발생했습니다: {str(e)}",
                    is_complete=True,
                    model=settings.model
                )
                yield f"data: {error_response.model_dump_json()}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"채팅 스트리밍 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"서버 오류: {str(e)}"
        )

@router.post("/extract-variables")
async def extract_variables(request: Dict[str, str]):
    """
    프롬프트에서 변수를 추출합니다.
    """
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(
                status_code=400, 
                detail="프롬프트가 필요합니다."
            )
        
        variables = PromptProcessor.extract_variables(prompt)
        variable_template = PromptProcessor.create_variable_template(prompt)
        
        return SuccessResponse(
            message="변수 추출 완료",
            data={
                "variables": variables,
                "template": variable_template,
                "count": len(variables)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"변수 추출 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"변수 추출 실패: {str(e)}"
        )

@router.post("/validate-variables")
async def validate_variables(request: Dict[str, Any]):
    """
    프롬프트와 제공된 변수를 검증합니다.
    """
    try:
        prompt = request.get("prompt", "")
        provided_variables = request.get("variables", {})
        
        if not prompt:
            raise HTTPException(
                status_code=400, 
                detail="프롬프트가 필요합니다."
            )
        
        missing_variables = PromptProcessor.validate_variables(
            prompt, 
            provided_variables
        )
        
        is_valid = len(missing_variables) == 0
        
        return SuccessResponse(
            message="변수 검증 완료",
            data={
                "is_valid": is_valid,
                "missing_variables": missing_variables,
                "missing_count": len(missing_variables)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"변수 검증 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"변수 검증 실패: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    채팅 서비스 헬스 체크
    """
    try:
        # LLM 서비스 상태 확인
        available_models = llm_service.get_available_models()
        total_models = sum(len(models) for models in available_models.values())
        
        return SuccessResponse(
            message="채팅 서비스 정상 작동",
            data={
                "status": "healthy",
                "available_models": total_models,
                "providers": list(available_models.keys())
            }
        )
        
    except Exception as e:
        logger.error(f"헬스 체크 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"서비스 오류: {str(e)}"
        ) 