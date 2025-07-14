from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import json
from dotenv import load_dotenv
import asyncio
from loguru import logger

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LLM Testing Tool API",
    description="확장된 LLM API 연동을 위한 백엔드 서버",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 임포트 및 등록
from app.routers import chat

app.include_router(chat.router)

# 기본 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "LLM Testing Tool API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-07-10T00:00:00Z"
    }

# 기본 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "LLM Testing Tool API v2.0",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "확장된 채팅 API",
            "변수 치환 기능",
            "고급 모델 파라미터",
            "시스템 프롬프트 지원"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-07-10T00:00:00Z",
        "version": "2.0.0"
    }

# 설정 정보 엔드포인트
@app.get("/api/config")
async def get_config():
    """현재 서버 설정 정보를 반환합니다."""
    from app.services.llm_service import llm_service
    
    try:
        available_models = llm_service.get_available_models()
        total_models = sum(len(models) for models in available_models.values())
    except:
        total_models = 0
    
    return {
        "backend_port": os.getenv("BACKEND_PORT", "8000"),
        "host": os.getenv("HOST", "0.0.0.0"),
        "cors_origins": os.getenv("CORS_ORIGINS", "http://localhost:5173"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "supported_models_count": total_models,
        "api_version": "2.0.0"
    }

# 서버 시작 시 실행
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 서버 시작: http://{host}:{port}")
    print(f"📖 API 문서: http://{host}:{port}/docs")
    print(f"🔧 디버그 모드: {debug}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 