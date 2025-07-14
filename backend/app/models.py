"""
LLM Testing Tool API 모델
확장된 API 스펙을 위한 Pydantic 모델 정의
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from enum import Enum

# 메시지 역할 열거형
class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    
    @classmethod
    def _missing_(cls, value):
        # 문자열 값으로도 열거형 생성 가능하도록
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        return None

# 기본 메시지 모델
class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        if v is None:
            return datetime.now()
        elif isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.now()
        return v

# 모델 설정 모델
class ModelSettings(BaseModel):
    model: str = Field(..., description="사용할 LLM 모델명")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="응답 창의성 조절 (0.0-2.0)")
    max_tokens: int = Field(2048, gt=0, le=200000, description="최대 토큰 수")
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling 파라미터")
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0, description="빈도 페널티")
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0, description="존재 페널티")
    stop: Optional[List[str]] = Field(None, description="중단 시퀀스 목록")
    
    @validator('model')
    def validate_model(cls, v):
        # llm_service.py에서 지원되는 모델 목록 가져오기
        try:
            from ..services.llm_service import llm_service
            supported_models = list(llm_service.get_supported_models().keys())
            if v not in supported_models:
                # 지원되지 않는 모델인 경우 경고만 출력하고 그대로 반환
                from loguru import logger
                logger.warning(f"지원되지 않는 모델: {v}, 기본값으로 처리")
                return v
            return v
        except ImportError:
            # llm_service를 가져올 수 없는 경우 (순환 참조 방지)
            from loguru import logger
            logger.warning(f"모델 검증 중 llm_service를 가져올 수 없음: {v}")
            return v
    
    @validator('temperature')
    def validate_temperature(cls, v, values):
        # 모델별 temperature 범위 검증
        try:
            from ..services.llm_service import llm_service
            model_name = values.get('model')
            if model_name:
                model_info = llm_service.get_model_info(model_name)
                if model_info:
                    min_temp, max_temp = model_info['temperature_range']
                    if v < min_temp or v > max_temp:
                        from loguru import logger
                        logger.warning(f"Temperature {v}가 모델 {model_name}의 범위({min_temp}~{max_temp})를 벗어남")
                        # 범위를 벗어나면 최대값으로 조정
                        return max(min_temp, min(v, max_temp))
        except (ImportError, KeyError, TypeError):
            pass
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v, values):
        # 모델별 max_tokens 범위 검증
        try:
            from ..services.llm_service import llm_service
            model_name = values.get('model')
            if model_name:
                model_info = llm_service.get_model_info(model_name)
                if model_info:
                    max_limit = model_info['max_tokens']
                    if v > max_limit:
                        from loguru import logger
                        logger.warning(f"Max tokens {v}가 모델 {model_name}의 최대값({max_limit})을 초과함")
                        # 최대값을 초과하면 최대값으로 조정
                        return max_limit
        except (ImportError, KeyError, TypeError):
            pass
        return v

# 확장된 채팅 요청 모델
class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="대화 메시지 목록")
    settings: ModelSettings = Field(..., description="모델 설정")
    system_prompt: Optional[str] = Field(None, description="시스템 프롬프트")
    variables: Optional[Dict[str, str]] = Field(None, description="변수 치환용 키-값 쌍")
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError("최소 하나의 메시지가 필요합니다.")
        
        # 사용자 메시지가 있는지 확인
        user_messages = [msg for msg in v if msg.role == MessageRole.USER]
        if not user_messages:
            raise ValueError("최소 하나의 사용자 메시지가 필요합니다.")
        
        return v

# 채팅 응답 청크 모델
class ChatResponseChunk(BaseModel):
    content: str = Field(..., description="응답 내용")
    is_complete: bool = Field(..., description="응답 완료 여부")
    model: str = Field(..., description="사용된 모델명")
    usage: Optional[Dict[str, Any]] = Field(None, description="토큰 사용량 정보")

# 모델 정보 모델
class ModelInfo(BaseModel):
    name: str = Field(..., description="모델명")
    provider: str = Field(..., description="제공업체 (openai/anthropic)")
    max_tokens: int = Field(..., description="최대 토큰 수")
    temperature_range: Tuple[float, float] = Field(..., description="온도 범위")
    description: str = Field(..., description="모델 설명")

# 사용 가능한 모델 목록 응답
class AvailableModelsResponse(BaseModel):
    models: Dict[str, ModelInfo] = Field(..., description="모델 정보 딕셔너리")
    total_count: int = Field(..., description="총 모델 수")

# 세션 컨텍스트 모델
class SessionContext(BaseModel):
    session_id: str = Field(..., description="세션 ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="메시지 히스토리")
    settings: ModelSettings = Field(..., description="세션 설정")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")

# 에러 응답 모델
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="에러 상세 메시지")
    error_code: Optional[str] = Field(None, description="에러 코드")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시간")

# 성공 응답 모델
class SuccessResponse(BaseModel):
    message: str = Field(..., description="성공 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="응답 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")

# 서버 설정 정보 모델
class ServerConfig(BaseModel):
    backend_port: str = Field(..., description="백엔드 포트")
    host: str = Field(..., description="호스트 주소")
    cors_origins: str = Field(..., description="CORS 허용 오리진")
    debug: bool = Field(..., description="디버그 모드 여부")
    environment: str = Field(..., description="환경 (development/production)")
    supported_models_count: int = Field(..., description="지원되는 모델 수") 