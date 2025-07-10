// API 서비스 모듈
// 백엔드 API 호출 및 스트리밍 응답 처리를 담당

// 타입 정의
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponseChunk {
  content: string;
  is_complete: boolean;
  model: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// API 기본 설정
const API_BASE_URL = '/api';

// 에러 처리 헬퍼 함수
function handleApiError(response: Response): Promise<ApiError> {
  return response.json().then((error: any) => ({
    detail: error.detail || '알 수 없는 오류가 발생했습니다.',
    status_code: response.status
  }));
}

// 일반 API 호출 헬퍼 함수
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw await handleApiError(response);
  }

  return response.json();
}

// 채팅 스트리밍 API 호출
export async function sendChatMessage(
  request: ChatRequest,
  onChunk: (chunk: ChatResponseChunk) => void,
  onError: (error: ApiError) => void,
  onComplete: () => void
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await handleApiError(response);
      onError(error);
      return;
    }

    // Server-Sent Events 스트리밍 처리
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('응답 스트림을 읽을 수 없습니다.');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        // 받은 데이터를 버퍼에 추가
        buffer += decoder.decode(value, { stream: true });
        
        // 완전한 SSE 메시지들을 처리
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 마지막 불완전한 라인은 버퍼에 보관

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onChunk(data as ChatResponseChunk);
            } catch (parseError) {
              console.warn('SSE 데이터 파싱 오류:', parseError);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    onComplete();
  } catch (error) {
    console.error('채팅 API 호출 오류:', error);
    onError({
      detail: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.',
      status_code: 500
    });
  }
}

// 서버 설정 정보 가져오기
export async function getServerConfig(): Promise<any> {
  return apiCall('/config');
}

// 헬스 체크
export async function healthCheck(): Promise<any> {
  return apiCall('/health');
}

// 서버 상태 확인
export async function checkServerStatus(): Promise<boolean> {
  try {
    await healthCheck();
    return true;
  } catch (error) {
    console.error('서버 연결 실패:', error);
    return false;
  }
} 