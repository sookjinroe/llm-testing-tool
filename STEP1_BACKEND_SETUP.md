# 1단계: 백엔드 환경 구축 작업 가이드

## 📋 작업 개요
LLM API 연동을 위한 기본 백엔드 환경을 구축하고, 프론트엔드와의 최소한의 연결을 구현합니다.

## 🎯 목표
- FastAPI 기반 백엔드 서버 구축
- LangChain + 벤더 SDK 설치
- 프론트엔드와의 기본 연결 구현
- 환경변수 관리 시스템 구축

## 📁 프로젝트 구조 (완료 후)
```
temp_test_tool_ui_svelte/
├── frontend/          # 기존 Svelte 앱 (현재 src/ 폴더)
│   ├── src/
│   ├── package.json
│   └── ...
├── backend/           # 새로 생성
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── __init__.py
│       ├── models.py
│       └── services/
└── README.md
```

## 🔧 단계별 작업

### 1단계: 프로젝트 구조 재구성 ✅ 완료
- [x] `src/` 폴더를 `frontend/src/`로 이동
- [x] `backend/` 폴더 생성
- [x] 기존 설정 파일들 `frontend/`로 이동
- 커밋 해시: 125febb
- 커밋 메시지: 1단계: 프로젝트 구조 재구성 및 프론트엔드 분리 완료 (STEP1_BACKEND_SETUP.md 문서화 포함)
- 커밋 일시: 2025-07-09 19:57:06 +0900

### 2단계: 백엔드 환경 구축 ✅ 완료
- [x] Python 가상환경 생성 (`backend/venv/`)
- [x] 가상환경 활성화
- [x] 핵심 라이브러리 설치
- [x] `requirements.txt` 생성
- 커밋 해시: 9d8c26c
- 커밋 메시지: 2단계: 백엔드 환경 구축 완료 (Python 가상환경, LangChain + FastAPI 설치)
- 커밋 일시: 2025-07-09 20:30:00 +0900

### 3단계: 기본 FastAPI 앱 구현 ✅ 완료
- [x] `backend/main.py` 생성
- [x] CORS 설정
- [x] 기본 `/api/chat-stream` 엔드포인트 구현
- [x] 환경변수 설정 (`.env`)
- 커밋 해시: 38f9ea4
- 커밋 메시지: 3단계: 기본 FastAPI 앱 구현 완료 (CORS 설정, 채팅 스트리밍 엔드포인트, 환경변수 로드)
- 커밋 일시: 2025-07-10 16:33:00 +0900

### 4단계: 프론트엔드 연결 ✅ 완료
- [x] Vite proxy 설정 업데이트
- [x] API 서비스 모듈 생성
- [x] 기존 채팅 컴포넌트와 연결
- 커밋 해시: (현재 작업 중)
- 커밋 메시지: 4단계: 프론트엔드 연결 완료 (API 서비스 모듈, 스트리밍 응답 처리, 에러 핸들링)
- 커밋 일시: 2025-07-10 17:15:00 +0900

### 5단계: 테스트 및 검증
- [ ] 백엔드 서버 실행 테스트
- [ ] 프론트엔드에서 API 호출 테스트
- [ ] 전체 플로우 검증

## 📦 설치할 라이브러리

### 백엔드 의존성
```bash
# 웹 프레임워크
fastapi
uvicorn

# LangChain + 벤더 SDK
langchain
langchain-openai
langchain-anthropic

# 유틸리티
python-dotenv
pydantic
```

## 🔑 환경변수 설정

### backend/.env
```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Server Settings
BACKEND_PORT=8000
HOST=0.0.0.0

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 🚀 실행 명령어

### 백엔드 서버 실행
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 개발 서버 실행
```bash
cd frontend
npm run dev
```

## ✅ 완료 기준

### 1단계 완료 기준 ✅
- [x] 프로젝트 구조가 frontend/와 backend/로 분리됨
- [x] 모든 프론트엔드 파일이 frontend/ 폴더에 정상 이동됨
- [x] 개발 서버가 정상 실행됨 (포트 5173)
- [x] npm install 및 의존성 재설치 완료

### 2단계 완료 기준 ✅
- [x] Python 가상환경이 backend/venv/에 정상 생성됨
- [x] 가상환경 활성화 및 pip 명령어 정상 작동
- [x] 핵심 라이브러리 설치 완료:
  - FastAPI (0.116.0) - 웹 프레임워크
  - Uvicorn (0.35.0) - ASGI 서버
  - LangChain (0.3.26) - LLM 프레임워크
  - LangChain-OpenAI (0.3.27) - OpenAI 연동
  - LangChain-Anthropic (0.3.17) - Anthropic 연동
  - Python-dotenv - 환경변수 관리
  - Pydantic (2.11.7) - 데이터 검증
- [x] requirements.txt 파일 생성 및 패키지 목록 저장
- [x] .gitignore에 Python 가상환경 및 환경변수 파일 제외 설정
- [x] 모든 패키지 버전 호환성 검토 완료 (안정적)

### 3단계 완료 기준 ✅
- [x] 백엔드 서버가 8000 포트에서 정상 실행
- [x] `/api/chat-stream` 엔드포인트 접근 가능 (에코 응답 구현)
- [x] 환경변수가 정상적으로 로드됨
- [x] CORS 설정으로 프론트엔드 연결 준비 완료
- [x] 모든 기본 엔드포인트 정상 동작:
  - GET / - 루트 엔드포인트
  - GET /health - 헬스 체크
  - GET /api/config - 설정 정보
  - POST /api/chat-stream - 채팅 스트리밍 (Server-Sent Events)

### 4단계 완료 기준 ✅
- [x] 프론트엔드에서 `/api/chat-stream` 호출 가능
- [x] 간단한 에코 응답이 프론트엔드에 표시
- [x] 스트리밍 응답이 실시간으로 표시됨
- [x] 에러 처리 및 로딩 상태 정상 동작
- [x] Vite proxy를 통한 백엔드 연결 성공

### 전체 완료 기준 (5단계 후)
- [ ] 전체 플로우 검증 완료
- [ ] 실제 LLM API 연동 준비 완료

## 🔄 다음 단계 준비
이 작업 완료 후:
- **4단계**: 프론트엔드 연결 (Vite proxy, API 서비스 모듈)
- **5단계**: 전체 플로우 테스트 및 검증
- **2단계**: 실제 LLM API 연동 (OpenAI/Anthropic)
- **3단계**: 고급 스트리밍 응답 구현 (Server-Sent Events)
- **4단계**: 에러 처리 및 로딩 상태 연동

## 📝 참고사항
- 모든 API 키는 `.env` 파일에 저장하고 `.gitignore`에 추가
- 개발 환경에서만 CORS를 허용하도록 설정
- 초기에는 간단한 에코 응답으로 연결 테스트
- 에러 처리는 기본적인 수준으로 시작

## 🎯 3단계 구현 세부사항

### 구현된 기능들
1. **FastAPI 앱 구조**: 기본 앱 생성 및 미들웨어 설정
2. **CORS 설정**: 프론트엔드(포트 5173)에서 요청 허용
3. **Pydantic 모델**: ChatMessage, ChatRequest, ChatResponse 정의
4. **엔드포인트 구현**:
   - `GET /` - 루트 엔드포인트 (API 정보)
   - `GET /health` - 헬스 체크
   - `GET /api/config` - 서버 설정 정보
   - `POST /api/chat-stream` - 채팅 스트리밍 (Server-Sent Events)
5. **스트리밍 응답**: SSE 형식으로 청크 단위 응답
6. **에러 처리**: HTTPException으로 적절한 에러 응답
7. **환경변수 로드**: python-dotenv로 .env 파일 로드

### 테스트 결과
- ✅ 서버 실행: http://localhost:8000 정상 동작
- ✅ API 문서: http://localhost:8000/docs 정상 표시
- ✅ 모든 엔드포인트 정상 응답
- ✅ 환경변수 정상 로드
- ✅ CORS 설정 정상 작동
