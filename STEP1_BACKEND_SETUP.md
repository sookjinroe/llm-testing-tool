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

### 2단계: 백엔드 환경 구축
- [ ] Python 가상환경 생성 (`backend/venv/`)
- [ ] 가상환경 활성화
- [ ] 핵심 라이브러리 설치
- [ ] `requirements.txt` 생성

### 3단계: 기본 FastAPI 앱 구현
- [ ] `backend/main.py` 생성
- [ ] CORS 설정
- [ ] 기본 `/api/chat-stream` 엔드포인트 구현
- [ ] 환경변수 설정 (`.env`)

### 4단계: 프론트엔드 연결
- [ ] Vite proxy 설정 업데이트
- [ ] API 서비스 모듈 생성
- [ ] 기존 채팅 컴포넌트와 연결

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

### 전체 완료 기준 (2-5단계 후)
- [ ] 백엔드 서버가 8000 포트에서 정상 실행
- [ ] 프론트엔드에서 `/api/chat-stream` 호출 가능
- [ ] 간단한 에코 응답이 프론트엔드에 표시
- [ ] 환경변수가 정상적으로 로드됨

## 🔄 다음 단계 준비
이 작업 완료 후:
- **2단계**: 실제 LLM API 연동 (OpenAI/Anthropic)
- **3단계**: 스트리밍 응답 구현 (Server-Sent Events)
- **4단계**: 에러 처리 및 로딩 상태 연동

## 📝 참고사항
- 모든 API 키는 `.env` 파일에 저장하고 `.gitignore`에 추가
- 개발 환경에서만 CORS를 허용하도록 설정
- 초기에는 간단한 에코 응답으로 연결 테스트
- 에러 처리는 기본적인 수준으로 시작
