<script lang="ts">
  import { currentSession, currentSettings, sessionStore } from '../../stores/sessions';
  import type { Variable, Settings } from '../../stores/sessions';
  import { getAvailableModels } from '../../services/api';
  import { onMount } from 'svelte';
  
  export let toggleSettingsPanel: () => void;
  
  $: currentSessionData = $currentSession;
  $: settings = $currentSettings;
  
  let showModelParams = false;
  let availableModels: any[] = [];
  let modelWarning = '';
  let rangeWarning = '';
  
  // 변경사항 감지 로직 제거 (실시간 적용으로 인해 불필요)
  
  // 앱 로드 시 백엔드 API에서 모델 목록과 범위 정보 가져오기
  onMount(async () => {
    try {
      const response = await getAvailableModels();
      if (response && response.models) {
        availableModels = Object.keys(response.models).map(modelName => ({
          value: modelName,
          label: modelName,
          provider: response.models[modelName].provider,
          max_tokens: response.models[modelName].max_tokens,
          temperature_range: response.models[modelName].temperature_range,
          description: response.models[modelName].description
        }));
      }
    } catch (error) {
      console.error('모델 목록 가져오기 실패:', error);
      // 실패 시 기본 모델 목록 사용
      availableModels = [
        { value: 'gpt-4o', label: 'GPT-4o', provider: 'openai', max_tokens: 128000, temperature_range: [0.0, 2.0] },
        { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet', provider: 'anthropic', max_tokens: 200000, temperature_range: [0.0, 1.0] }
      ];
    }
  });
  
  // 현재 선택된 모델의 정보 가져오기
  $: currentModelInfo = availableModels.find(m => m.value === settings.model.model);
  
  // 현재 모델의 범위 정보
  $: temperatureRange = currentModelInfo?.temperature_range || [0.0, 2.0];
  $: maxTokensLimit = currentModelInfo?.max_tokens || 8192;
  
  // 모델 변경 시 지원 여부 확인 및 범위 검증
  function checkModelSupport(modelName: string) {
    const isSupported = availableModels.some(model => model.value === modelName);
    if (!isSupported && availableModels.length > 0) {
      modelWarning = `지원되지 않는 모델: ${modelName}`;
    } else {
      modelWarning = '';
    }
    
    // 범위 검증
    checkRangeValidation();
  }
  
  // 범위 검증 및 경고 표시
  function checkRangeValidation() {
    if (!currentModelInfo) return;
    
    const warnings = [];
    
    // Temperature 범위 검증
    if (settings.model.temperature < temperatureRange[0] || settings.model.temperature > temperatureRange[1]) {
      warnings.push(`Temperature는 ${temperatureRange[0]}~${temperatureRange[1]} 범위여야 합니다.`);
    }
    
    // Max Tokens 범위 검증
    if (settings.model.maxTokens > maxTokensLimit) {
      warnings.push(`Max Tokens는 ${maxTokensLimit} 이하여야 합니다.`);
    }
    
    rangeWarning = warnings.join(' ');
  }
  
  // 모델 변경 시 범위에 맞춰 값 자동 조정
  function adjustValuesToRange() {
    if (!currentModelInfo) return;
    
    let hasAdjustment = false;
    
    // Temperature 범위 조정
    if (settings.model.temperature > temperatureRange[1]) {
      settings.model.temperature = temperatureRange[1];
      hasAdjustment = true;
    } else if (settings.model.temperature < temperatureRange[0]) {
      settings.model.temperature = temperatureRange[0];
      hasAdjustment = true;
    }
    
    // Max Tokens 범위 조정
    if (settings.model.maxTokens > maxTokensLimit) {
      settings.model.maxTokens = maxTokensLimit;
      hasAdjustment = true;
    }
    
    if (hasAdjustment) {
      rangeWarning = `값이 ${currentModelInfo.label}의 범위에 맞춰 자동 조정되었습니다.`;
      setTimeout(() => { rangeWarning = ''; }, 3000); // 3초 후 경고 제거
    }
  }
  
  // 프롬프트에서 변수 추출하는 함수
  function extractVariablesFromPrompt(text: string): string[] {
    const regex = /\{\{([^}]+)\}\}/g;
    const matches: string[] = [];
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
  
  function updateModelSetting(key: string, value: any) {
    updateCurrentSettings(s => ({
      ...s,
      model: { ...s.model, [key]: value }
    }));
    
    // 모델 변경 시 지원 여부 확인 및 범위 조정
    if (key === 'model') {
      checkModelSupport(value);
      // 모델 변경 후 약간의 지연을 두고 범위 조정 (반응형 업데이트 대기)
      setTimeout(() => {
        adjustValuesToRange();
      }, 100);
    }
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
  
  // 설정 적용/초기화 함수 제거 (실시간 적용으로 인해 불필요)
  
  // 이벤트 핸들러 함수들
  function handleModelChange(e: Event) {
    const target = e.target as HTMLSelectElement;
    updateModelSetting('model', target.value);
  }
  
  function handleTemperatureChange(e: Event) {
    const target = e.target as HTMLInputElement;
    updateModelSetting('temperature', parseFloat(target.value));
  }
  
  // Max Tokens 포커스 아웃 시 처리
  function handleMaxTokensBlur(e: Event) {
    const target = e.target as HTMLInputElement;
    const value = parseInt(target.value) || 1; // 기본값 1
    
    // 값 반영
    updateModelSetting('maxTokens', value);
    
    // 포커스 아웃 시 범위 검증 및 자동 조정
    setTimeout(() => {
      adjustValuesToRange();
    }, 0);
  }
  
  // Max Tokens 엔터 키 처리
  function handleMaxTokensKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      (e.target as HTMLInputElement).blur(); // 포커스 아웃
    }
  }
  
  function handleTopPChange(e: Event) {
    const target = e.target as HTMLInputElement;
    updateModelSetting('topP', parseFloat(target.value));
  }
  
  function handleSystemPromptChange(e: Event) {
    const target = e.target as HTMLTextAreaElement;
    updateSystemPrompt(target.value);
  }
  
  function handleVariableChange(index: number, field: 'name' | 'value', e: Event) {
    const target = e.target as HTMLInputElement;
    updateVariable(index, field, target.value);
  }
  
  // 현재 모델 지원 여부 확인 (반응형)
  $: if (settings.model.model) {
    checkModelSupport(settings.model.model);
  }
  
  // 범위 검증 (반응형)
  $: if (currentModelInfo) {
    checkRangeValidation();
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
            on:change={handleModelChange}
          >
            {#each availableModels as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
          {#if modelWarning}
            <div class="model-warning">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 9v2m0 4h.01M9 10h.01"/>
              </svg>
              {modelWarning}
            </div>
          {/if}
          {#if rangeWarning}
            <div class="range-warning">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 9v2m0 4h.01M9 10h.01"/>
              </svg>
              {rangeWarning}
            </div>
          {/if}
        </div>
        
        {#if showModelParams}
          <div class="model-params">
            <div class="form-group">
              <label class="label" for="temperature">
                Temperature: {settings.model.temperature}
                {#if currentModelInfo}
                  <small class="text-muted">({temperatureRange[0]}~{temperatureRange[1]})</small>
                {/if}
              </label>
              <input 
                id="temperature"
                type="range" 
                min={temperatureRange[0]} 
                max={temperatureRange[1]} 
                step="0.1"
                value={settings.model.temperature}
                on:input={handleTemperatureChange}
                class="range-input"
              />
            </div>
            
            <div class="form-group">
              <label class="label" for="max-tokens">
                Max Tokens
                {#if currentModelInfo}
                  <small class="text-muted">(최대 {maxTokensLimit.toLocaleString()})</small>
                {/if}
              </label>
              <input 
                id="max-tokens"
                type="number" 
                min="1" 
                max={maxTokensLimit}
                value={settings.model.maxTokens}
                on:blur={handleMaxTokensBlur}
                on:keydown={handleMaxTokensKeydown}
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
                on:input={handleTopPChange}
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
            on:input={handleSystemPromptChange}
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
                  on:input={(e) => handleVariableChange(index, 'value', e)}
                />
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
    
    <!-- 초기화/적용 버튼 제거 (실시간 적용으로 인해 불필요) -->
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

  /* 초기화/적용 버튼 스타일 제거 (실시간 적용으로 인해 불필요) */

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

  .model-warning {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    margin-top: var(--space-2);
    padding: var(--space-1) var(--space-2);
    background-color: var(--vscode-warning-bg);
    color: var(--vscode-warning-fg);
    border-radius: 6px;
    border: 1px solid var(--vscode-warning-border);
    font-size: 12px;
  }
  
  .range-warning {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    margin-top: var(--space-2);
    padding: var(--space-1) var(--space-2);
    background-color: var(--vscode-info-bg);
    color: var(--vscode-info-fg);
    border-radius: 6px;
    border: 1px solid var(--vscode-info-border);
    font-size: 12px;
  }
</style>