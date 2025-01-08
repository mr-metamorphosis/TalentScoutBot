import { create } from 'zustand';

export interface CandidateInfo {
  name: string;
  experienceYears: number;
  techStack: string[];
  position: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatState {
  candidateInfo: CandidateInfo | null;
  messages: ChatMessage[];
  isInterviewStarted: boolean;
  setCandidateInfo: (info: CandidateInfo) => void;
  addMessage: (message: ChatMessage) => void;
  startInterview: () => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  candidateInfo: null,
  messages: [],
  isInterviewStarted: false,
  setCandidateInfo: (info) => set({ candidateInfo: info }),
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message]
  })),
  startInterview: () => set({ isInterviewStarted: true }),
  reset: () => set({ 
    candidateInfo: null, 
    messages: [], 
    isInterviewStarted: false 
  })
}));
