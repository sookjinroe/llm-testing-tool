<script lang="ts">
  import SessionHistory from './components/SessionHistory.svelte';
  import ChatView from './components/chat/ChatView.svelte';
  import SettingsPanel from './components/chat/SettingsPanel.svelte';
  import ProjectView from './components/ProjectView.svelte';
  import LibraryView from './components/LibraryView.svelte';
  import { sessionStore, currentSession, isCurrentSessionDraft } from './stores/sessions';
  import { onMount } from 'svelte';
  
  let currentView = 'chat'; // 'chat', 'project', 'library'
  
  $: currentSessionData = $currentSession;
  $: isDraft = $isCurrentSessionDraft;
  
  // 앱 초기화 시 새 초안 세션 생성
  onMount(() => {
    sessionStore.createNewSession();
  });
  
  function createNewSession() {
    sessionStore.createNewSession();
    currentView = 'chat';
  }
  
  function setView(view: string) {
    currentView = view;
    // 다른 뷰로 이동할 때 현재 세션 비활성화
    if (view !== 'chat') {
      sessionStore.selectSession(null);
    }
  }
  
  // 설정 패널 상태 관리
  let settingsPanelCollapsed = true;
  
  function toggleSettingsPanel() {
    settingsPanelCollapsed = !settingsPanelCollapsed;
  }
  
  // 세션 선택 시 채팅 뷰로 이동
  function handleSessionSelect() {
    currentView = 'chat';
  }
</script>

<main class="app-container">
  <!-- Left Panel: Navigation & History -->
  <aside class="sidebar">
    <!-- Navigation Menu -->
    <nav class="navigation">
      <button 
        class="nav-item" 
        class:active={currentView === 'chat' && isDraft}
        on:click={createNewSession}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span>새 채팅</span>
      </button>
      
      <button 
        class="nav-item" 
        class:active={currentView === 'project'}
        on:click={() => setView('project')}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <span>프로젝트</span>
      </button>
      
      <button 
        class="nav-item" 
        class:active={currentView === 'library'}
        on:click={() => setView('library')}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
        </svg>
        <span>라이브러리</span>
      </button>
      
      <div class="nav-divider"></div>
      
      <div class="nav-section-header">
        <span>최근 대화</span>
      </div>
      
      <!-- History Sessions (always visible) -->
      <div class="history-sessions">
        <SessionHistory {handleSessionSelect} />
      </div>
    </nav>
  </aside>

  <!-- Main Content Area -->
  <div class="content-wrapper">
    <main class="editor-area">
      <div class="view-container">
        {#if currentView === 'chat'}
          <div class="chat-and-settings-layout">
            <div class="chat-section">
              <ChatView {toggleSettingsPanel} {settingsPanelCollapsed} />
            </div>
            
            <div class="settings-section" class:collapsed={settingsPanelCollapsed}>
              <SettingsPanel {toggleSettingsPanel} />
            </div>
          </div>
        {:else if currentView === 'project'}
          <ProjectView />
        {:else if currentView === 'library'}
          <LibraryView />
        {/if}
      </div>
    </main>
  </div>
</main>

<style>
  .app-container {
    display: flex;
    height: 100vh;
    background: var(--vscode-bg-primary);
  }

  .content-wrapper {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .sidebar {
    width: 280px;
    background: var(--vscode-sidebar-bg);
    border-right: 1px solid var(--vscode-border);
    display: flex;
    flex-direction: column;
  }

  .navigation {
    flex: 1;
    padding: var(--space-2);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .nav-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    margin-bottom: var(--space-1);
    border: none;
    background: transparent;
    color: var(--vscode-text-primary);
    font-size: 13px;
    font-family: inherit;
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: all 0.1s ease;
    text-align: left;
  }

  .nav-item:hover {
    background: var(--vscode-bg-tertiary);
  }

  .nav-item.active {
    background: var(--vscode-selection-bg);
    color: var(--vscode-text-primary);
  }

  .nav-item svg {
    flex-shrink: 0;
    color: var(--vscode-text-muted);
  }

  .nav-item.active svg {
    color: var(--vscode-text-primary);
  }

  .nav-item:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .nav-item:disabled:hover {
    background: transparent;
  }

  .nav-divider {
    height: 1px;
    background: var(--vscode-border);
    margin: var(--space-4) 0 var(--space-3) 0;
  }

  .nav-section-header {
    padding: 0 var(--space-3) var(--space-2) var(--space-3);
    font-size: 11px;
    font-weight: 600;
    color: var(--vscode-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .history-sessions {
    flex: 1;
    overflow-y: auto;
  }

  .editor-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: var(--vscode-panel-bg);
  }

  .view-container {
    flex: 1;
    overflow: hidden;
  }

  .chat-and-settings-layout {
    height: 100%;
    display: flex;
    overflow: hidden;
  }

  .chat-section {
    flex: 1;
    transition: all 0.3s ease;
    overflow: hidden;
  }

  .settings-section {
    width: 350px;
    transition: all 0.3s ease;
    overflow: hidden;
    border-left: 1px solid var(--vscode-border);
  }

  .settings-section.collapsed {
    width: 0;
    border-left: none;
  }

  @media (max-width: 1200px) {
    .settings-section {
      width: 300px;
    }
  }

  @media (max-width: 900px) {
    .settings-section {
      width: 280px;
    }
  }
</style>