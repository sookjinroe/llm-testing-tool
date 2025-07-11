# 2단계: LLM API 연동 및 스펙 확장 작업 가이드

## 📋 작업 개요
STEP1에서 구축한 기본 백엔드 환경을 바탕으로 실제 LLM API(OpenAI, Anthropic) 연동을 구현하고, 프론트엔드에서 필요한 고급 기능들을 위한 API 스펙을 확장합니다.

## 🎯 목표
- LangChain 기반 LLM API 연동 구현
- 현재 에코 응답을 실제 LLM 응답으로 교체
- API 스펙 확장 (모델 선택, 파라미터 조정 등)
- 에러 처리 및 재시도 로직 강화
- 응답 품질 및 성능 최적화
- 향후 확장을 위한 모듈화된 구조 구축

## 📁 프로젝트 구조 (완료 후)
```
temp_test_tool_ui_svelte/
├── frontend/          # 기존 Svelte 앱
│   ├── src/
│   │   ├── services/
│   │   │   └── api.ts          # API 서비스 (업데이트)
│   │   └── ...
│   └── ...
├── backend/           # 백엔드 (확장)
│   ├── main.py                # 메인 앱 (업데이트)
│   ├── requirements.txt       # 의존성 (업데이트)
│   ├── .env                   # 환경변수 (API 키 추가)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py          # Pydantic 모델 (확장)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py # LLM API 연동 서비스
│   │   │   └── error_handler.py # 에러 처리
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── chat.py        # 채팅 관련 라우터
│   └── venv/
└── README.md
```

## 🔧 단계별 작업

### 1단계: LangChain 기반 LLM 서비스 모듈 구현 ✅ 완료
- [x] `backend/app/services/llm_service.py` 생성
- [x] LangChain LLM 클라이언트 설정 (OpenAI, Anthropic)
- [x] 모델별 파라미터 매핑 구현
- [x] 스트리밍 응답 처리 로직 구현
- [x] 모델 팩토리 패턴으로 확장성 확보

### 2단계: API 스펙 확장
- [ ] Pydantic 모델 확장 (`backend/app/models.py`)
- [ ] 모델 선택 옵션 추가
- [ ] 고급 파라미터 지원 (temperature, max_tokens, top_p 등)
- [ ] 시스템 프롬프트 지원
- [ ] 변수 치환 기능 구현
- [ ] 세션 컨텍스트 처리 (메시지 히스토리 포함)

### 3단계: 에러 처리 및 재시도 로직
- [ ] `backend/app/services/error_handler.py` 생성
- [ ] API 키 검증 로직
- [ ] 네트워크 오류 처리
- [ ] 재시도 로직 구현
- [ ] 사용자 친화적 에러 메시지

### 4단계: 메인 앱 업데이트
- [ ] `backend/main.py` 리팩토링
- [ ] 라우터 구조로 변경
- [ ] LLM 서비스 통합
- [ ] 에러 핸들러 적용
- [ ] 로깅 시스템 추가

### 5단계: 프론트엔드 연동 업데이트
- [ ] `frontend/src/services/api.ts` 업데이트
- [ ] 새로운 API 스펙에 맞춘 요청 형식 수정
- [ ] 에러 처리 개선
- [ ] 로딩 상태 개선

## 📦 추가 설치할 라이브러리

### 백엔드 의존성 (추가)
```bash
# 로깅 및 모니터링
loguru

# 재시도 로직
tenacity

# 비동기 처리
aiohttp

# 환경변수 검증
pydantic-settings
```

## 🔑 환경변수 설정 (확장)

### backend/.env (업데이트)
```env
# API Keys (필수)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Server Settings
BACKEND_PORT=8000
HOST=0.0.0.0

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# LLM Settings
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048

# Error Handling
MAX_RETRIES=3
RETRY_DELAY=1.0

# Logging
LOG_LEVEL=INFO
```

## 🚀 실행 명령어

### 백엔드 서버 실행 (동일)
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 개발 서버 실행 (동일)
```bash
cd frontend
npm run dev
```

## ✅ 완료 기준

### 1단계 완료 기준
- [x] `llm_service.py` 파일이 생성되고 LangChain 기반 구조 구현
- [x] OpenAI 모델 (gpt-4, gpt-3.5-turbo) 연동이 정상 작동
- [x] Anthropic 모델 (claude-3-sonnet, claude-3-haiku) 연동이 정상 작동
- [x] 스트리밍 응답이 실제 LLM에서 오는지 확인
- [ ] 에코 응답이 실제 LLM 응답으로 교체됨 (4단계에서 처리)
- [x] 새로운 모델 추가 시 설정만으로 확장 가능한지 확인

### 2단계 완료 기준
- [ ] Pydantic 모델이 확장되어 모델 선택 옵션 지원
- [ ] 고급 파라미터들이 API 요청에서 정상 처리됨
- [ ] 시스템 프롬프트가 LLM에 전달됨
- [ ] 변수 치환이 정상 작동함
- [ ] API 문서에서 새로운 스펙이 확인됨

### 3단계 완료 기준
- [ ] API 키가 없을 때 적절한 에러 메시지 표시
- [ ] 네트워크 오류 시 재시도 로직 작동
- [ ] 사용자 친화적 에러 메시지가 프론트엔드에 표시됨
- [ ] 로그 파일에 에러 정보가 기록됨

### 4단계 완료 기준
- [ ] 메인 앱이 라우터 구조로 리팩토링됨
- [ ] LLM 서비스가 메인 앱에 통합됨
- [ ] 에러 핸들러가 모든 엔드포인트에 적용됨
- [ ] 로깅 시스템이 정상 작동함

### 5단계 완료 기준
- [ ] 프론트엔드에서 새로운 API 스펙으로 요청 가능
- [ ] 에러 처리가 개선되어 사용자에게 명확한 메시지 표시
- [ ] 로딩 상태가 실제 API 호출 시간에 맞춰 표시됨
- [ ] 전체 플로우가 정상 작동함

## 🔄 다음 단계 준비
이 작업 완료 후:
- **3단계**: 고급 기능 구현 (세션 저장/로드, 프로젝트 관리)
- **4단계**: 성능 최적화 및 모니터링
- **5단계**: 배포 준비 및 문서화

## 📝 참고사항
- API 키는 반드시 `.env` 파일에 저장하고 `.gitignore`에 추가
- 실제 API 호출 시 비용이 발생하므로 테스트 시 주의
- 에러 처리 시 민감한 정보가 노출되지 않도록 주의
- 로그 파일에 API 키나 민감한 정보가 기록되지 않도록 주의
- **세션 관리**: 현재는 프론트엔드에서 메모리 기반으로 관리, 향후 백엔드 저장 기능 추가 예정

## 🎯 구현 방향

### LangChain 기반 LLM 서비스 구조
- **모델 팩토리 패턴**: 새로운 모델 추가 시 설정만 변경
- **통일된 스트리밍**: LangChain의 `astream` 메서드 활용
- **메시지 변환**: LangChain의 표준 메시지 형식 사용
- **확장 가능한 구조**: 향후 LangChain의 고급 기능 활용 가능

### 지원 모델
- **OpenAI**: gpt-4, gpt-3.5-turbo
- **Anthropic**: claude-3-sonnet, claude-3-haiku
- **확장 가능**: 새로운 모델 추가 시 딕셔너리에만 추가

### 확장된 API 스펙
- **모델 선택**: OpenAI, Anthropic 모델 지원
- **고급 파라미터**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty
- **시스템 프롬프트**: LLM 동작 제어를 위한 시스템 메시지
- **변수 치환**: 프롬프트 내 변수 동적 치환
- **세션 컨텍스트**: 메시지 히스토리 포함

### 에러 처리 구조
- **API 키 검증**: 유효하지 않은 API 키 처리
- **네트워크 오류**: 연결 실패 시 재시도 로직
- **사용자 친화적 메시지**: 기술적 오류를 이해하기 쉬운 메시지로 변환
- **로깅 시스템**: 오류 추적을 위한 로그 기록

## 🧪 테스트 계획

### 기본 기능 테스트
- **LangChain 연동**: OpenAI, Anthropic 모델 정상 작동 확인
- **스트리밍 응답**: 실시간 토큰 스트리밍 확인
- **모델 전환**: 다양한 모델 간 전환 확인
- **파라미터 조정**: temperature, max_tokens 등 파라미터 적용 확인

### 에러 처리 테스트
- **API 키 오류**: 잘못된 키에 대한 적절한 처리
- **네트워크 오류**: 연결 실패 시 재시도 로직
- **토큰 제한**: max_tokens 초과 시 처리

### 성능 목표
- **응답 시간**: 첫 토큰까지 2초 이내
- **에러율**: 1% 이하
- **재시도 성공률**: 90% 이상 