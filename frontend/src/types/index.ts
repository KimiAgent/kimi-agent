export type Role = "user" | "assistant" | "system";

export interface Message {
  role: Role;
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  use_search?: boolean;
  stream?: boolean;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  sources?: string[];
  tool_calls?: string[];
}

export interface UploadResponse {
  session_id: string;
  file_name: string;
  message: string;
  summary: string;
}

export interface HistoryResponse {
  session_id: string;
  messages: Message[];
  total: number;
}

export interface HealthResponse {
  status: string;
  model: string;
  version: string;
}
