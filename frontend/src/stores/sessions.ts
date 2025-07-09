import { writable, derived } from 'svelte/store';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ModelSettings {
  model: string;
  temperature: number;
  maxTokens: number;
  topP: number;
  frequencyPenalty: number;
  presencePenalty: number;
}

export interface Variable {
  name: string;
  value: string;
}

export interface Settings {
  model: ModelSettings;
  systemPrompt: string;
  variables: Variable[];
}

export interface Session {
  id: string;
  title: string;
  messages: Message[];
  settings: Settings;
  isLoading: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Default settings
export const defaultSettings: Settings = {
  model: {
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 2048,
    topP: 1.0,
    frequencyPenalty: 0,
    presencePenalty: 0
  },
  systemPrompt: '',
  variables: []
};

// 단일 원천 스토어들 (직접 쓰기 가능)
export const sessionsStore = writable<Session[]>([]);
export const currentSessionId = writable<string | null>(null);

// 초안 세션 스토어 (전역 배열에 포함되지 않음)
export const draftSession = writable<Session | null>(null);

// 파생 스토어들 (읽기 전용)
export const currentSession = derived(
  [sessionsStore, currentSessionId, draftSession],
  ([sessions, sessionId, draft]) => {
    if (!sessionId) return null;
    
    // 초안 세션인지 확인
    if (draft && draft.id === sessionId) {
      return draft;
    }
    
    // 일반 세션에서 찾기
    return sessions.find(s => s.id === sessionId) || null;
  }
);

export const currentSettings = derived(
  currentSession,
  (session) => session?.settings || defaultSettings
);

// Session management functions
export const sessionStore = {
  subscribe: currentSession.subscribe,
  
  createNewSession: () => {
    const newDraftSession: Session = {
      id: crypto.randomUUID(),
      title: '새 대화',
      messages: [],
      settings: JSON.parse(JSON.stringify(defaultSettings)), // Deep copy of default settings
      isLoading: false,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    // 초안으로 설정하고 현재 세션으로 선택 (아직 sessionsStore에는 추가하지 않음)
    draftSession.set(newDraftSession);
    currentSessionId.set(newDraftSession.id);
  },
  
  selectSession: (sessionId: string | null) => {
    currentSessionId.set(sessionId);
  },
  
  addMessage: (sessionId: string, message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date()
    };
    
    if (!sessionId) return;
    
    // 현재 초안 세션과 일반 세션 상태 확인
    let currentDraft: Session | null = null;
    draftSession.subscribe(draft => currentDraft = draft)();
    
    // 초안 세션에 첫 메시지를 추가하는 경우
    if (currentDraft && currentDraft.id === sessionId) {
      const isFirstMessage = currentDraft.messages.length === 0;
      const updatedSession: Session = {
        ...currentDraft,
        messages: [...currentDraft.messages, newMessage],
        updatedAt: new Date(),
        title: isFirstMessage ? 
          (currentDraft.title === '새 대화' ? 
            message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '') : 
            currentDraft.title) : 
          currentDraft.title
      };
      
      if (isFirstMessage) {
        // 첫 메시지인 경우: 초안을 sessionsStore에 추가하고 초안 스토어는 클리어
        sessionsStore.update(sessions => [updatedSession, ...sessions]);
        draftSession.set(null);
      } else {
        // 첫 메시지가 아닌 경우: 초안 업데이트
        draftSession.set(updatedSession);
      }
    } else {
      // 일반 세션 업데이트
      sessionsStore.update(sessions => {
        return sessions.map(session => {
          if (session.id === sessionId) {
            return {
              ...session,
              messages: [...session.messages, newMessage],
              updatedAt: new Date()
            };
          }
          return session;
        });
      });
    }
  },
  
  deleteSession: (sessionId: string) => {
    // 초안 세션 삭제 확인
    let currentDraft: Session | null = null;
    draftSession.subscribe(draft => currentDraft = draft)();
    
    if (currentDraft && currentDraft.id === sessionId) {
      // 초안 세션 삭제
      draftSession.set(null);
      currentSessionId.set(null);
      return;
    }
    
    // 일반 세션 삭제
    sessionsStore.update(sessions => sessions.filter(s => s.id !== sessionId));
    
    // 현재 세션이 삭제된 세션이면 null로 설정
    currentSessionId.update(currentId => 
      currentId === sessionId ? null : currentId
    );
  },
  
  // 로딩 상태 업데이트
  updateSessionLoadingState: (sessionId: string, loading: boolean) => {
    // 초안 세션 로딩 상태 업데이트
    draftSession.update(draft => {
      if (draft && draft.id === sessionId) {
        return { ...draft, isLoading: loading };
      }
      return draft;
    });
    
    // 일반 세션 로딩 상태 업데이트
    sessionsStore.update(sessions => 
      sessions.map(s => s.id === sessionId ? { ...s, isLoading: loading } : s)
    );
  },
  
  // 현재 세션의 설정 업데이트
  updateSessionSettings: (updater: (settings: Settings) => Settings) => {
    let currentId: string | null = null;
    currentSessionId.subscribe(id => currentId = id)();
    
    if (!currentId) return;
    
    // 초안 세션 설정 업데이트
    draftSession.update(draft => {
      if (draft && draft.id === currentId) {
        const updatedSettings = updater(draft.settings);
        return {
          ...draft,
          settings: updatedSettings,
          updatedAt: new Date()
        };
      }
      return draft;
    });
    
    // 일반 세션 설정 업데이트
    sessionsStore.update(sessions => {
      return sessions.map(session => {
        if (session.id === currentId) {
          const updatedSettings = updater(session.settings);
          return {
            ...session,
            settings: updatedSettings,
            updatedAt: new Date()
          };
        }
        return session;
      });
    });
  },
  
  // 세션 제목 변경
  renameSession: (sessionId: string, newTitle: string) => {
    // 초안 세션 제목 업데이트
    draftSession.update(draft => {
      if (draft && draft.id === sessionId) {
        return {
          ...draft,
          title: newTitle,
          updatedAt: new Date()
        };
      }
      return draft;
    });
    
    // 일반 세션 제목 업데이트
    sessionsStore.update(sessions => {
      return sessions.map(session => {
        if (session.id === sessionId) {
          return {
            ...session,
            title: newTitle,
            updatedAt: new Date()
          };
        }
        return session;
      });
    });
  }
};

// 초안 세션 관련 유틸리티
export const draftSessionStore = {
  subscribe: draftSession.subscribe,
  
  // 현재 세션이 초안인지 확인
  isDraft: (sessionId: string | null): boolean => {
    if (!sessionId) return false;
    
    let currentDraft: Session | null = null;
    draftSession.subscribe(draft => currentDraft = draft)();
    
    return currentDraft?.id === sessionId;
  },
  
  // 초안 세션 클리어
  clearDraft: () => {
    draftSession.set(null);
  }
};

// 현재 세션이 초안인지 확인하는 파생 스토어
export const isCurrentSessionDraft = derived(
  [currentSessionId, draftSession],
  ([sessionId, draft]) => {
    if (!sessionId || !draft) return false;
    return draft.id === sessionId;
  }
);

// 메시지가 있는 세션들만 필터링하는 파생 스토어 (History에 표시용)
export const sessionsWithMessages = derived(
  sessionsStore,
  (sessions) => sessions.filter(session => session.messages.length > 0)
);

// 하위 호환성을 위한 별칭들 (기존 코드가 동작하도록)
export const currentSessionStore = currentSession;
export const settingsStore = currentSettings;