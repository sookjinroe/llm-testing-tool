<script lang="ts">
  import { currentSession, currentSettings, sessionStore } from '../../stores/sessions';
  import type { Variable, Settings } from '../../stores/sessions';
  
  export let toggleSettingsPanel: () => void;
  
  $: currentSessionData = $currentSession;
  $: settings = $currentSettings;
  
  let showModelParams = false;
  
  // 초기 설정값 저장 (변경사항 감지용)
  let initialSettings: Settings | null = null;
  
  // 세션이 변경될 때마다 초기 설정값 업데이트
  $: if (currentSessionData && JSON.stringify(currentSessionData.settings) !== JSON.stringify(initialSettings)) {
    initialSettings = JSON.parse(JSON.stringify(currentSessionData.settings));
  }
  
  // 변경사항이 있는지 확인
  $: hasChanges = initialSettings && currentSessionData ? 
    JSON.stringify(settings) !== JSON.stringify(initialSettings) : false;
  
  // 프롬프트에서 변수 추출하는 함수
  function extractVariablesFromPrompt(text: string): string[] {
    const regex = /\{\{([^}]+)\}\}/g;
    const matches = [];
    let match;
    
    while ((match = regex.exec(text)) !== null) {
      const varName = match[1].trim();
      if (varName && !matches.includes(varName)) {
        matches.push(varName);
      }
    }
    
    return matches;
  }
  
  // 프롬프트 변경 시 변수 자동 업데이트
  function updateSystemPrompt(value: string) {
    if (!currentSessionData) return;
    
    updateCurrentSettings(s => ({ ...s, systemPrompt: value }));
    
    // 프롬프트에서 변수 추출
    const extractedVars = extractVariablesFromPrompt(value);
    
    // 기존 변수와 비교하여 새로운 변수만 추가
    updateCurrentSettings(s => {
      const existingVarNames = s.variables.map(v => v.name);
      const newVars = extractedVars
        .filter(varName => !existingVarNames.includes(varName))
        .map(varName => ({ name: varName, value: '' }));
      
      return {
        ...s,
        variables: [...s.variables, ...newVars]
      };
    });
  }
  
  // 현재 세션 설정 업데이트 헬퍼 함수
  function updateCurrentSettings(updater: (settings: Settings) => Settings) {
    if (!currentSessionData) return;
    sessionStore.updateSessionSettings(updater);
  }
  
  const modelOptions = [
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'claude-3-opus', label: 'Claude 3 Opus' },
    { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
    { value: 'claude-3-haiku', label: 'Claude 3 Haiku' }
  ];
  
  function updateModelSetting(key: string, value: any) {
    updateCurrentSettings(s => ({
      ...s,
      model: { ...s.model, [key]: value }
    }));
  }
  
  function updateVariable(index: number, field: 'name' | 'value', value: string) {
    updateCurrentSettings(s => ({
      ...s,
      variables: s.variables.map((v, i) => 
        i === index ? { ...v, [field]: value } : v
      )
    }));
  }
  
  function removeVariable(index: number) {
    updateCurrentSettings(s => ({
      ...s,
      variables: s.variables.filter((_, i) => i !== index)
    }));
  }
  
  // 설정 적용
  function applySettings() {
    if (currentSessionData && initialSettings) {
      initialSettings = JSON.parse(JSON.stringify(currentSessionData.settings));
    }
    console.log('설정이 적용되었습니다:', settings);
  }
  
  // 설정 초기화
  function resetSettings() {
    if (initialSettings && currentSessionData) {
      updateCurrentSettings(() => JSON.parse(JSON.stringify(initialSettings)));
    }
  }
</script>

<div class="settings-panel">
  <div class="settings-header">
    <h2>설정</h2>
    <button 
      class="btn btn-icon close-button"
      on:click={toggleSettingsPanel}
      title="설정 패널 닫기"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6L6 18M6 6l12 12"/>
      </svg>
    </button>
  </div>
  
  {#if currentSessionData}
    <div class="settings-content">
      <!-- Model Selection Section -->
      <div class="settings-section">
        <div class="section-header">
          <h3>모델 설정</h3>
          <button 
            class="btn btn-icon params-toggle"
            on:click={() => showModelParams = !showModelParams}
            title="파라미터 {showModelParams ? '숨기기' : '보기'}"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" 
                 style="transform: rotate({showModelParams ? 180 : 0}deg); transition: transform 0.2s ease;">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </button>
        </div>
        
        <div class="form-group">
          <label class="label" for="model-select">모델</label>
          <select 
            id="model-select"
            class="select rounded-input"
            value={settings.model.model}
            on:change={(e) => updateModelSetting('model', e.target.value)}
          >
            {#each modelOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>
        
        {#if showModelParams}
          <div class="model-params">
            <div class="form-group">
              <label class="label" for="temperature">Temperature: {settings.model.temperature}</label>
              <input 
                id="temperature"
                type="range" 
                min="0" 
                max="2" 
                step="0.1"
                value={settings.model.temperature}
                on:input={(e) => updateModelSetting('temperature', parseFloat(e.target.value))}
                class="range-input"
              />
            </div>
            
            <div class="form-group">
              <label class="label" for="max-tokens">Max Tokens</label>
              <input 
                id="max-tokens"
                type="number" 
                min="1" 
                max="8192"
                value={settings.model.maxTokens}
                on:input={(e) => updateModelSetting('maxTokens', parseInt(e.target.value))}
                class="input rounded-input"
              />
            </div>
            
            <div class="form-group">
              <label class="label" for="top-p">Top P: {settings.model.topP}</label>
              <input 
                id="top-p"
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                value={settings.model.topP}
                on:input={(e) => updateModelSetting('topP', parseFloat(e.target.value))}
                class="range-input"
              />
            </div>
          </div>
        {/if}
      </div>

      <!-- System Prompt Section -->
      <div class="settings-section">
        <div class="section-header">
          <h3>시스템 프롬프트</h3>
        </div>
        
        <div class="form-group">
          <div class="prompt-help">
            <small class="text-muted">변수는 &#123;&#123;변수명&#125;&#125; 형태로 입력하세요</small>
          </div>
          <textarea 
            id="system-prompt"
            class="input textarea rounded-input"
            placeholder="시스템 프롬프트를 입력하세요... 예: 당신은 &#123;&#123;role&#125;&#125;입니다."
            value={settings.systemPrompt}
            on:input={(e) => updateSystemPrompt(e.target.value)}
          ></textarea>
        </div>
      </div>

      <!-- Variables Section -->
      {#if settings.variables.length > 0}
        <div class="settings-section">
          <div class="section-header">
            <h3>변수 값</h3>
            <small class="text-muted">프롬프트에서 자동으로 감지된 변수들</small>
          </div>
          
          <div class="variables-list">
            {#each settings.variables as variable, index}
              <div class="variable-item">
                <div class="variable-info">
                  <label class="variable-label">&#123;&#123;{variable.name}&#125;&#125;</label>
                  <button 
                    class="btn btn-icon btn-sm"
                    on:click={() => removeVariable(index)}
                    title="변수 삭제"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
                <input 
                  type="text" 
                  class="input rounded-input"
                  placeholder="값을 입력하세요"
                  value={variable.value}
                  on:input={(e) => updateVariable(index, 'value', e.target.value)}
                />
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
    
    <!-- Apply/Reset Buttons (only show when there are changes) -->
    {#if hasChanges}
      <div class="settings-actions">
        <button class="btn rounded-btn" on:click={resetSettings}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1-6.74 2.74L21 8"/>
            <path d="M21 3v5h-5"/>
            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
            <path d="M3 21v-5h5"/>
          </svg>
          초기화
        </button>
        <button class="btn btn-primary rounded-btn" on:click={applySettings}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
          적용
        </button>
      </div>
    {/if}
  {:else}
    <div class="no-session-content">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 1v6m0 6v6"/>
          <path d="m21 12-6-6-6 6-6-6"/>
        </svg>
      </div>
      <h3>설정을 사용하려면</h3>
      <p>먼저 대화를 선택하거나 새 대화를 시작하세요.</p>
    </div>
  {/if}
</div>

<style>
  .settings-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--vscode-panel-bg);
    overflow: hidden;
  }

  .settings-header {
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-4);
    border-bottom: 1px solid var(--vscode-border);
    background: var(--vscode-bg-secondary);
  }

  .settings-header h2 {
    font-size: 14px;
    font-weight: 600;
    color: var(--vscode-text-primary);
  }

  .close-button {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid var(--vscode-input-border);
    background: var(--vscode-input-bg);
    color: var(--vscode-text-secondary);
    transition: all 0.2s ease;
  }

  .close-button:hover {
    background: var(--vscode-bg-tertiary);
    color: var(--vscode-text-primary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }

  .settings-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .settings-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: var(--space-2);
    border-bottom: 1px solid var(--vscode-border);
  }

  .section-header h3 {
    font-size: 13px;
    font-weight: 600;
    color: var(--vscode-text-primary);
  }

  .form-group {
    margin-bottom: var(--space-3);
  }

  .form-group:last-child {
    margin-bottom: 0;
  }

  .params-toggle {
    height: 28px;
    width: 28px;
    flex-shrink: 0;
    border: 1px solid var(--vscode-input-border);
    border-radius: 6px;
  }

  .prompt-help {
    margin-bottom: var(--space-2);
  }

  .model-params {
    margin-top: var(--space-3);
    padding-left: var(--space-4);
    border-left: 2px solid var(--vscode-border);
  }

  /* Rounded input styles */
  .rounded-input {
    border-radius: 8px;
    border: 1px solid var(--vscode-input-border);
    background: var(--vscode-input-bg);
    transition: all 0.2s ease;
  }

  .rounded-input:focus {
    border-color: var(--vscode-focus-border);
    box-shadow: 0 0 0 2px rgba(0, 125, 212, 0.1);
  }

  .rounded-btn {
    border-radius: 8px;
    transition: all 0.2s ease;
  }

  .rounded-btn:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }

  .range-input {
    width: 100%;
    height: 4px;
    border-radius: 2px;
    background: var(--vscode-input-border);
    outline: none;
    -webkit-appearance: none;
  }

  .range-input::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--vscode-accent);
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .range-input::-moz-range-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--vscode-accent);
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .variables-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .variable-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-2) 0;
    border-bottom: 1px solid var(--vscode-border-light);
  }

  .variable-item:last-child {
    border-bottom: none;
  }

  .variable-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .variable-label {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 12px;
    color: var(--vscode-accent);
    background: var(--vscode-bg-secondary);
    padding: var(--space-1) var(--space-2);
    border-radius: 4px;
    border: 1px solid var(--vscode-border);
  }

  .textarea {
    min-height: 120px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    line-height: 1.4;
    resize: vertical;
  }

  .settings-actions {
    display: flex;
    gap: var(--space-2);
    padding: var(--space-4);
    border-top: 1px solid var(--vscode-border);
    background: var(--vscode-bg-secondary);
    justify-content: flex-end;
  }

  .settings-actions .btn {
    min-width: 80px;
  }

  .no-session-content {
    flex: 1;
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