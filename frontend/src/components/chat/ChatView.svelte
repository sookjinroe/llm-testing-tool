<script lang="ts">
  import ChatArea from './ChatArea.svelte';
  import { currentSession, sessionStore } from '../../stores/sessions';
  
  export let toggleSettingsPanel: () => void;
  export let settingsPanelCollapsed: boolean;
  
  $: currentSessionData = $currentSession;
  
  // 제목 편집 상태
  let editing = false;
  let draftTitle = '';
  
  function startEditing() {
    if (!currentSessionData) return;
    editing = true;
    draftTitle = currentSessionData.title;
  }
  
  function saveTitle() {
    if (!currentSessionData || !draftTitle.trim()) {
      cancelEditing();
      return;
    }
    
    sessionStore.renameSession(currentSessionData.id, draftTitle.trim());
    editing = false;
  }
  
  function cancelEditing() {
    editing = false;
    draftTitle = '';
  }
  
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      saveTitle();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      cancelEditing();
    }
  }
</script>

<div class="chat-view">
  <div class="view-header">
    <div class="view-title">
      {#if editing}
        <input
          type="text"
          class="title-input"
          bind:value={draftTitle}
          on:keydown={handleKeydown}
          on:blur={saveTitle}
          placeholder="제목을 입력하세요"
          autofocus
        />
      {:else}
        <h2>{currentSessionData?.title || '새 대화'}</h2>
        {#if currentSessionData}
          <button 
            class="btn btn-icon edit-title-btn" 
            on:click={startEditing}
            title="제목 편집"
            aria-label="Edit title"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
        {/if}
      {/if}
    </div>
    <div class="view-actions">
      {#if settingsPanelCollapsed}
        <button 
          class="btn btn-icon" 
          on:click={toggleSettingsPanel} 
          title="설정 패널 열기"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
        </button>
      {/if}
    </div>
  </div>
  
  <div class="chat-container">
    {#key $currentSession?.id}
      <ChatArea />
    {/key}
  </div>
</div>

<style>
  .chat-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--vscode-panel-bg);
  }

  .view-header {
    height: 48px;
    background: var(--vscode-panel-bg);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-4);
    border-bottom: 1px solid var(--vscode-border);
  }

  .view-title {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: center;
  }
  
  .view-title h2 {
    display: inline;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    color: var(--vscode-text-primary);
    letter-spacing: 0.5px;
    max-width: calc(100% - 32px); /* 편집 버튼 공간 확보 */
  }
  
  .title-input {
    width: 100%;
    padding: var(--space-1) var(--space-2);
    border: 1px solid var(--vscode-focus-border);
    border-radius: var(--radius-sm);
    background: var(--vscode-input-bg);
    color: var(--vscode-text-primary);
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    outline: none;
  }
  
  .edit-title-btn {
    opacity: 0;
    width: 24px;
    height: 24px;
    padding: var(--space-1);
    transition: opacity 0.2s ease;
    margin-left: var(--space-1);
  }
  
  .view-title:hover .edit-title-btn {
    opacity: 1;
  }

  .view-actions {
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .chat-container {
    flex: 1;
    overflow: hidden;
  }
</style>