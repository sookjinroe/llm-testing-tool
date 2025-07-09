<script lang="ts">
  import { afterUpdate } from 'svelte';
  import { currentSession } from '../../stores/sessions';
  import ChatMessages from './ChatMessages.svelte';
  import ChatInput from './ChatInput.svelte';
  
  $: currentSessionData = $currentSession;
  
  let chatContainer: HTMLElement;
  
  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }
  
  // DOM 업데이트 후 자동으로 스크롤
  afterUpdate(scrollToBottom);
  
  function handleMessageSent() {
    // afterUpdate에서 자동으로 처리되므로 별도 호출 불필요
  }
</script>

<div class="chat-area">
  {#if currentSessionData}
    <ChatMessages session={currentSessionData} bind:chatContainer />
    <ChatInput session={currentSessionData} onMessageSent={handleMessageSent} />
  {:else}
    <div class="no-session">
      <div class="no-session-content">
        <div class="no-session-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <h3>대화를 선택하세요</h3>
        <p>왼쪽에서 기존 대화를 선택하거나 새 대화를 시작하세요.</p>
      </div>
    </div>
  {/if}
</div>

<style>
  .chat-area {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--vscode-panel-bg);
  }

  .no-session {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .no-session-content {
    text-align: center;
    padding: var(--space-8);
    color: var(--vscode-text-muted);
  }

  .no-session-icon {
    margin-bottom: var(--space-4);
    opacity: 0.5;
  }

  .no-session-content h3 {
    font-size: 18px;
    font-weight: 500;
    color: var(--vscode-text-primary);
    margin-bottom: var(--space-2);
  }

  .no-session-content p {
    font-size: 14px;
    color: var(--vscode-text-secondary);
  }
</style>