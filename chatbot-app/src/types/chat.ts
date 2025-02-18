export interface Message {
    role: 'user' | 'assistant';
    content: string;
  }
  
  export interface ChatResponse {
    response: string;
    error?: string;
  }