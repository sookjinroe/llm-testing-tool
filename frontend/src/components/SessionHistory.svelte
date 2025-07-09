<script lang="ts">
  import { sessionsWithMessages, currentSession, sessionStore } from '../stores/sessions';
  import type { Session } from '../stores/sessions';
  
  export let handleSessionSelect: () => void;
  
  $: sessions = $sessionsWithMessages;
  $: currentSessionData = $currentSession;
  
  function selectSession(session: Session) {
    sessionStore.selectSession(session.id);
    handleSessionSelect();
  }
  
  function deleteSession(sessionId: string, event: Event) {
    event.stopPropagation();
    sessionStore.deleteSession(sessionId);
  }
  
  function formatDate(date: Date) {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return '오늘';
    } else if (days === 1) {
      return '어제';
    } else if (days < 7) {
      return `${days}일 전`;
    } else {
      return date.toLocaleDateString('ko-KR', { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  }
</script>

<div class="session-history">
    {#each sessions as session (session.id)}
      <div 
        class="session-item" 
        class:active={currentSessionData?.id === session.id}
        on:click={() => selectSession(session)}
        role="button"
        tabindex="0"
        on:keydown={(e) => e.key === 'Enter' && selectSession(session)}
      >
        <div class="session-content">
          <div class="session-title">{session.title}</div>
        </div>
        
        <button 
          class="delete-btn"
          on:click={(e) => deleteSession(session.id, e)}
          title="대화 삭제"
          aria-label="Delete session"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c0-1 1-2 2-2v2"/>
          </svg>
        </button>
      </div>
    {/each}
    
    {#if sessions.length === 0}
      <div class="empty-state">
        <p>대화가 없습니다</p>
        <p class="text-muted text-sm">새 대화를 시작해보세요</p>
      </div>
    {/if}
</div>

<style>
  .session-history {
    padding: var(--space-1) 0;
  }

  .session-item {
    display: flex;
    align-items: center;
    padding: var(--space-2);
    margin-bottom: var(--space-1);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background-color 0.1s ease;
    position: relative;
  }

  .session-item:hover {
    background: var(--vscode-bg-tertiary);
  }

  .session-item.active {
    background: var(--vscode-selection-bg);
    color: var(--vscode-text-primary);
  }

  .session-content {
    flex: 1;
    min-width: 0;
  }

  .session-title {
    font-size: 13px;
    font-weight: 400;
    color: var(--vscode-text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .delete-btn {
    opacity: 0;
    padding: var(--space-1);
    border: none;
    background: none;
    color: var(--vscode-text-muted);
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: all 0.1s ease;
    flex-shrink: 0;
  }

  .session-item:hover .delete-btn {
    opacity: 1;
  }

  .delete-btn:hover {
    background: var(--vscode-bg-tertiary);
    color: var(--vscode-text-primary);
  }

  .empty-state {
    text-align: center;
    padding: var(--space-4) var(--space-2);
    color: var(--vscode-text-muted);
  }

  .empty-state p {
    font-size: 12px;
    margin-bottom: var(--space-2);
  }

  .empty-state p:first-of-type {
    color: var(--vscode-text-secondary);
  }
</style>