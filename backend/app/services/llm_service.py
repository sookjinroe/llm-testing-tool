"""
LangChain 기반 LLM API 연동 서비스
OpenAI와 Anthropic의 최신 모델을 지원하는 통합 LLM 서비스
"""

import os
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional, List
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# 최신 모델 설정 (2025년 1월 기준 - 실제 API 조회 결과)
SUPPORTED_MODELS = {
    # OpenAI 모델 (실제 API 조회 결과)
    "gpt-4o": {
        "provider": "openai",
        "model": "gpt-4o",
        "max_tokens": 128000,
        "temperature_range": (0.0, 2.0),
        "description": "OpenAI 멀티모달 GPT-4o 모델 (최대 128K 토큰)"
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "max_tokens": 128000,
        "temperature_range": (0.0, 2.0),
        "description": "OpenAI 경량 멀티모달 모델 (최대 128K 토큰)"
    },
    "o3-mini": {
        "provider": "openai",
        "model": "o3-mini",
        "max_tokens": 128000,
        "temperature_range": (0.0, 2.0),
        "description": "OpenAI 최적화 모델 (최대 128K 토큰)"
    },
    "gpt-4.5-preview": {
        "provider": "openai",
        "model": "gpt-4.5-preview",
        "max_tokens": 128000,
        "temperature_range": (0.0, 2.0),
        "description": "OpenAI GPT-4.5 프리뷰 모델 (최대 128K 토큰)"
    },
    "gpt-4.1": {
        "provider": "openai",
        "model": "gpt-4.1",
        "max_tokens": 128000,
        "temperature_range": (0.0, 2.0),
        "description": "OpenAI GPT-4.1 모델 (최대 128K 토큰)"
    },
    "gpt-4.1-mini": {
        "provider": "openai",
        "model": "gpt-4.1-mini",
        "max_tokens": 128000,
        "temperature_range": (0.0, 2.0),
        "description": "OpenAI GPT-4.1 미니 모델 (최대 128K 토큰)"
    },
    
    # Anthropic 모델 (실제 API 조회 결과)
    "claude-opus-4-20250514": {
        "provider": "anthropic",
        "model": "claude-opus-4-20250514",
        "max_tokens": 200000,
        "temperature_range": (0.0, 1.0),
        "description": "Anthropic Claude 4 Opus (최고 성능, 최대 200K 토큰)"
    },
    "claude-sonnet-4-20250514": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 200000,
        "temperature_range": (0.0, 1.0),
        "description": "Anthropic Claude 4 Sonnet (최대 200K 토큰)"
    },
    "claude-3-7-sonnet-20250219": {
        "provider": "anthropic",
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 200000,
        "temperature_range": (0.0, 1.0),
        "description": "Anthropic Claude 3.7 Sonnet (최대 200K 토큰)"
    },
    "claude-3-5-haiku-20241022": {
        "provider": "anthropic",
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 200000,
        "temperature_range": (0.0, 1.0),
        "description": "Anthropic Claude 3.5 Haiku (빠른 응답, 최대 200K 토큰)"
    },
    "claude-3-opus-20240229": {
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "max_tokens": 200000,
        "temperature_range": (0.0, 1.0),
        "description": "Anthropic Claude 3 Opus (최고 성능, 최대 200K 토큰, 2026년 1월 5일까지 지원)"
    }
}

class LLMServiceError(Exception):
    """LLM 서비스 관련 예외"""
    pass

class LLMService:
    """LangChain 기반 LLM 서비스"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.default_temperature = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
        self.default_max_tokens = int(os.getenv("DEFAULT_MAX_TOKENS", "2048"))
        
        # API 키 검증
        self._validate_api_keys()
        
        # LLM 클라이언트 초기화
        self._init_clients()
    
    def _validate_api_keys(self):
        """API 키 유효성 검증"""
        if not self.openai_api_key:
            logger.warning("OpenAI API 키가 설정되지 않았습니다.")
        
        if not self.anthropic_api_key:
            logger.warning("Anthropic API 키가 설정되지 않았습니다.")
        
        if not self.openai_api_key and not self.anthropic_api_key:
            raise LLMServiceError("최소 하나의 API 키가 필요합니다.")
    
    def _init_clients(self):
        """LLM 클라이언트 초기화"""
        self.clients = {}
        
        # OpenAI 클라이언트
        if self.openai_api_key:
            self.clients["openai"] = ChatOpenAI(
                api_key=self.openai_api_key,
                model=self.default_model,  # 명시적으로 모델 지정
                temperature=self.default_temperature,
                max_tokens=self.default_max_tokens,
                streaming=True
            )
            logger.info("OpenAI 클라이언트 초기화 완료")
        
        # Anthropic 클라이언트
        if self.anthropic_api_key:
            # SUPPORTED_MODELS에서 Anthropic 모델의 실제 엔진명 가져오기
            anthropic_model = "claude-3-5-sonnet-20241022"  # 기본값 (실제 조회된 정보)
            if self.default_model in SUPPORTED_MODELS:
                model_info = SUPPORTED_MODELS[self.default_model]
                if model_info["provider"] == "anthropic":
                    anthropic_model = model_info["model"]
            
            self.clients["anthropic"] = ChatAnthropic(
                api_key=self.anthropic_api_key,
                model=anthropic_model,  # SUPPORTED_MODELS의 실제 엔진명 사용
                temperature=self.default_temperature,
                max_tokens=self.default_max_tokens,
                streaming=True
            )
            logger.info("Anthropic 클라이언트 초기화 완료")
    
    def get_supported_models(self) -> Dict[str, Dict[str, Any]]:
        """지원되는 모델 목록 반환"""
        return SUPPORTED_MODELS
    
    def validate_model(self, model_name: str) -> bool:
        """모델명 유효성 검증"""
        return model_name in SUPPORTED_MODELS
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """모델 정보 반환"""
        return SUPPORTED_MODELS.get(model_name)
    
    def _convert_messages_to_langchain(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """메시지를 LangChain 형식으로 변환"""
        langchain_messages = []
        
        for message in messages:
            role = message.get("role", "").lower()
            content = message.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        return langchain_messages
    
    def _get_client_for_model(self, model_name: str):
        """모델에 해당하는 클라이언트 반환 (기존 방식)"""
        if not self.validate_model(model_name):
            raise LLMServiceError(f"지원되지 않는 모델: {model_name}")
        
        model_info = SUPPORTED_MODELS[model_name]
        provider = model_info["provider"]
        
        if provider not in self.clients:
            raise LLMServiceError(f"{provider} 클라이언트가 초기화되지 않았습니다.")
        
        return self.clients[provider]
    
    def _create_fresh_client_for_model(self, model_name: str, temperature: float, max_tokens: int):
        """모델에 해당하는 fresh 클라이언트 생성 (권장 방식)"""
        if not self.validate_model(model_name):
            raise LLMServiceError(f"지원되지 않는 모델: {model_name}")
        
        model_info = SUPPORTED_MODELS[model_name]
        provider = model_info["provider"]
        model_engine = model_info["model"]
        
        if provider == "openai":
            if not self.openai_api_key:
                raise LLMServiceError("OpenAI API 키가 설정되지 않았습니다.")
            return ChatOpenAI(
                api_key=self.openai_api_key,
                model=model_engine,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=True
            )
        elif provider == "anthropic":
            if not self.anthropic_api_key:
                raise LLMServiceError("Anthropic API 키가 설정되지 않았습니다.")
            return ChatAnthropic(
                api_key=self.anthropic_api_key,
                model=model_engine,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=True
            )
        else:
            raise LLMServiceError(f"지원되지 않는 provider: {provider}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model_name: str = None,
        temperature: float = None,
        max_tokens: int = None,
        system_prompt: str = None
    ) -> AsyncGenerator[str, None]:
        """
        LLM 응답 생성 (스트리밍)
        
        Args:
            messages: 대화 메시지 목록
            model_name: 사용할 모델명
            temperature: 온도 설정
            max_tokens: 최대 토큰 수
            system_prompt: 시스템 프롬프트
        
        Yields:
            str: 스트리밍 응답 청크
        """
        try:
            # 기본값 설정
            model_name = model_name or self.default_model
            temperature = temperature if temperature is not None else self.default_temperature
            max_tokens = max_tokens or self.default_max_tokens
            
            # 모델 정보 가져오기
            model_info = self.get_model_info(model_name)
            if not model_info:
                raise LLMServiceError(f"지원되지 않는 모델: {model_name}")
            
            # Fresh 클라이언트 생성 (권장 방식)
            client = self._create_fresh_client_for_model(model_name, temperature, max_tokens)
            
            # 메시지 변환
            langchain_messages = self._convert_messages_to_langchain(messages)
            
            # 시스템 프롬프트 추가
            if system_prompt:
                langchain_messages.insert(0, SystemMessage(content=system_prompt))
            
            logger.info(f"모델 {model_name}으로 응답 생성 시작")
            
            # 스트리밍 응답 생성
            async for chunk in client.astream(langchain_messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
            
            logger.info(f"모델 {model_name} 응답 생성 완료")
            
        except Exception as e:
            logger.error(f"LLM 응답 생성 중 오류: {str(e)}")
            raise LLMServiceError(f"응답 생성 실패: {str(e)}")
    
    async def generate_single_response(
        self,
        messages: List[Dict[str, str]],
        model_name: str = None,
        temperature: float = None,
        max_tokens: int = None,
        system_prompt: str = None
    ) -> str:
        """
        LLM 응답 생성 (단일 응답)
        
        Args:
            messages: 대화 메시지 목록
            model_name: 사용할 모델명
            temperature: 온도 설정
            max_tokens: 최대 토큰 수
            system_prompt: 시스템 프롬프트
        
        Returns:
            str: 완전한 응답
        """
        try:
            # 기본값 설정
            model_name = model_name or self.default_model
            temperature = temperature if temperature is not None else self.default_temperature
            max_tokens = max_tokens or self.default_max_tokens
            
            # 모델 정보 가져오기
            model_info = self.get_model_info(model_name)
            if not model_info:
                raise LLMServiceError(f"지원되지 않는 모델: {model_name}")
            
            # Fresh 클라이언트 생성 (권장 방식)
            client = self._create_fresh_client_for_model(model_name, temperature, max_tokens)
            
            # 메시지 변환
            langchain_messages = self._convert_messages_to_langchain(messages)
            
            # 시스템 프롬프트 추가
            if system_prompt:
                langchain_messages.insert(0, SystemMessage(content=system_prompt))
            
            logger.info(f"모델 {model_name}으로 단일 응답 생성 시작")
            
            # 응답 생성
            response = await client.ainvoke(langchain_messages)
            
            logger.info(f"모델 {model_name} 단일 응답 생성 완료")
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM 단일 응답 생성 중 오류: {str(e)}")
            raise LLMServiceError(f"응답 생성 실패: {str(e)}")
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """사용 가능한 모델 목록 반환"""
        available_models = {
            "openai": [],
            "anthropic": []
        }
        
        for model_name, model_info in SUPPORTED_MODELS.items():
            provider = model_info["provider"]
            if provider in self.clients:
                available_models[provider].append(model_name)
        
        return available_models

# 전역 LLM 서비스 인스턴스
llm_service = LLMService() 