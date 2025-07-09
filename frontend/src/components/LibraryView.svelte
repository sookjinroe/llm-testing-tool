<div class="library-view">
  <div class="view-header">
    <div class="view-title">
      <h2>라이브러리</h2>
    </div>
  </div>
  
  <div class="view-content">
    <div class="empty-content">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
        </svg>
      </div>
      <h3>라이브러리 기능</h3>
      <p>개발 예정입니다.</p>
    </div>
  </div>
</div>

<style>
  .library-view {
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

  .view-title h2 {
    font-size: 13px;
    font-weight: 600;
    color: var(--vscode-text-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .view-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4);
  }

  .empty-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: var(--space-8);
    color: var(--vscode-text-muted);
  }

  .empty-icon {
    margin-bottom: var(--space-4);
    opacity: 0.5;
  }

  .empty-content h3 {
    font-size: 18px;
    font-weight: 500;
    color: var(--vscode-text-primary);
    margin-bottom: var(--space-2);
  }

  .empty-content p {
    font-size: 14px;
    color: var(--vscode-text-secondary);
  }
</style>