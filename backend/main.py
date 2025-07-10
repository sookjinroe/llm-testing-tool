from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from dotenv import load_dotenv
import asyncio

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LLM Testing Tool API",
    description="LLM API 연동을 위한 백엔드 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048

class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[dict] = None

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

# 채팅 스트리밍 엔드포인트
@app.post("/api/chat-stream")
async def chat_stream(request: ChatRequest):
    """
    채팅 메시지를 받아서 스트리밍 응답을 반환합니다.
    현재는 에코 응답으로 구현되어 있습니다.
    """
    try:
        # 마지막 사용자 메시지 추출
        user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                user_message = message.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="사용자 메시지가 없습니다.")
        
        # 에코 응답 생성 (실제 LLM API 연동 전 테스트용)
        echo_response = f"에코 응답: {user_message}"
        
        # 스트리밍 응답 생성
        async def generate_response():
            # 응답을 여러 청크로 나누어 스트리밍
            chunks = [echo_response[i:i+20] for i in range(0, len(echo_response), 20)]
            
            for i, chunk in enumerate(chunks):
                # SSE 형식으로 데이터 전송
                data = {
                    "content": chunk,
                    "is_complete": i == len(chunks) - 1,
                    "model": request.model
                }
                
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                # 실제 LLM API 호출 시에는 여기서 지연이 발생
                await asyncio.sleep(0.1)
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 설정 정보 엔드포인트
@app.get("/api/config")
async def get_config():
    """현재 서버 설정 정보를 반환합니다."""
    return {
        "backend_port": os.getenv("BACKEND_PORT", "8000"),
        "host": os.getenv("HOST", "0.0.0.0"),
        "cors_origins": os.getenv("CORS_ORIGINS", "http://localhost:5173"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "environment": os.getenv("ENVIRONMENT", "development")
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