<script lang="ts">
  import { tick } from 'svelte';
  import { sessionStore } from '../../stores/sessions';
  import type { Session } from '../../stores/sessions';
  import { sendChatMessage, type ChatRequest, type ChatMessage as ApiChatMessage } from '../../services/api';
  
  export let session: Session;
  export let onMessageSent: () => void = () => {};
  
  let messageInput = '';
  let currentSessionId = session.id;
  let isStreaming = false;
  let streamingContent = '';
  
  // 세션이 변경되면 입력창 초기화
  $: if (session.id !== currentSessionId) {
    messageInput = '';
    currentSessionId = session.id;
    streamingContent = '';
  }
  
  async function sendMessage() {
    if (!messageInput.trim() || !session || session.isLoading || isStreaming) return;
    
    const userMessage = messageInput.trim();
    const sessionId = session.id;
    messageInput = '';
    
    // DOM 업데이트 완료까지 대기하여 플래시 현상 방지
    await tick();
    
    // Add user message
    sessionStore.addMessage(sessionId, {
      role: 'user',
      content: userMessage
    });
    
    onMessageSent();
    
    // 실제 API 호출
    sessionStore.updateSessionLoadingState(sessionId, true);
    isStreaming = true;
    streamingContent = '';
    
    try {
      // API 요청 데이터 준비 - 현재 세션의 메시지 + 새로 추가된 사용자 메시지
      const currentMessages = session.messages.map(msg => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content
      }));
      
      // 새로 추가된 사용자 메시지도 포함
      currentMessages.push({
        role: 'user',
        content: userMessage
      });
      
      const request: ChatRequest = {
        messages: currentMessages,
        model: session.settings.model.model,
        temperature: session.settings.model.temperature,
        max_tokens: session.settings.model.maxTokens
      };
      
      // 스트리밍 응답 처리
      await sendChatMessage(
        request,
        // onChunk: 각 청크 처리
        (chunk) => {
          streamingContent += chunk.content;
          // 실시간으로 메시지 업데이트 (스트리밍 중)
          sessionStore.updateStreamingMessage(sessionId, streamingContent);
          onMessageSent();
        },
        // onError: 에러 처리
        (error) => {
          console.error('API 호출 오류:', error);
          sessionStore.addMessage(sessionId, {
            role: 'assistant',
            content: `오류가 발생했습니다: ${error.detail}`
          });
          sessionStore.updateSessionLoadingState(sessionId, false);
          onMessageSent();
        },
        // onComplete: 완료 처리
        () => {
          // 스트리밍 완료 시 로딩 상태만 해제 (메시지는 이미 updateStreamingMessage에서 추가됨)
          sessionStore.updateSessionLoadingState(sessionId, false);
          streamingContent = '';
          onMessageSent();
        }
      );
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      sessionStore.addMessage(sessionId, {
        role: 'assistant',
        content: '메시지 전송 중 오류가 발생했습니다.'
      });
      sessionStore.updateSessionLoadingState(sessionId, false);
      onMessageSent();
    } finally {
      isStreaming = false;
    }
  }
  
  // 줄바꿈만 차단 (keydown)
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // 줄바꿈만 차단
    }
  }
  
  // 실제 전송 처리 (keyup)
  function handleKeyup(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      // IME 조합이 완료된 후에만 전송
      if (!session?.isLoading) {
        sendMessage();
      }
    }
  }
</script>

<div class="input-area">
  <div class="input-container">
    <div class="message-input-wrapper">
      <textarea
        bind:value={messageInput}
        on:keydown={handleKeydown}
        on:keyup={handleKeyup}
        placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
        class="message-input"
        rows="1"
      ></textarea>
      
      <button 
        class="send-button"
        on:click={sendMessage}
        disabled={!messageInput.trim() || session?.isLoading}
        title="메시지 전송"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
        </svg>
      </button>
    </div>
  </div>
</div>

<style>
  .input-area {
    padding: var(--space-4);
    background: var(--vscode-panel-bg);
  }

  .input-container {
    max-width: 800px;
    margin: 0 auto;
  }

  .message-input-wrapper {
    display: flex;
    align-items: end;
    gap: var(--space-3);
    padding: var(--space-3);
    background: var(--vscode-bg-secondary);
    border: 1px solid var(--vscode-border);
    border-radius: 16px;
    transition: all 0.2s ease;
  }

  .message-input-wrapper:focus-within {
    border-color: var(--vscode-focus-border);
    box-shadow: 0 0 0 2px rgba(0, 125, 212, 0.1);
  }

  .message-input {
    flex: 1;
    min-height: 24px;
    max-height: 200px;
    border: none;
    background: transparent;
    color: var(--vscode-text-primary);
    font-size: 14px;
    font-family: inherit;
    resize: none;
    outline: none;
    line-height: 1.4;
  }

  .message-input::placeholder {
    color: var(--vscode-text-muted);
  }

  .send-button {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 8px;
    background: var(--vscode-button-bg);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .send-button:hover:not(:disabled) {
    background: var(--vscode-button-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }

  .send-button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
</style>