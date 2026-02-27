import axios, { AxiosInstance } from "axios";
import FormData from "form-data";
import fs from "fs";
import path from "path";

import type {
  ChatRequest,
  ChatResponse,
  UploadResponse,
  HistoryResponse,
  HealthResponse,
} from "../types/index.js";

export class KimiAgentClient {
  private http: AxiosInstance;

  constructor(baseUrl?: string) {
    this.http = axios.create({
      baseURL: baseUrl || process.env.API_BASE_URL || "http://localhost:8000",
      headers: { "Content-Type": "application/json" },
      timeout: 60_000,
    });
  }

  // ------------------------------------------------------------------ //
  //  Health                                                              //
  // ------------------------------------------------------------------ //

  async health(): Promise<HealthResponse> {
    const { data } = await this.http.get<HealthResponse>("/health");
    return data;
  }

  // ------------------------------------------------------------------ //
  //  Chat                                                                //
  // ------------------------------------------------------------------ //

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const { data } = await this.http.post<ChatResponse>("/chat", request);
    return data;
  }

  async newSession(): Promise<string> {
    const { data } = await this.http.get<{ session_id: string }>("/sessions/new");
    return data.session_id;
  }

  // ------------------------------------------------------------------ //
  //  File upload                                                         //
  // ------------------------------------------------------------------ //

  async uploadFile(sessionId: string, filePath: string): Promise<UploadResponse> {
    const form = new FormData();
    form.append("session_id", sessionId);
    form.append("file", fs.createReadStream(filePath), {
      filename: path.basename(filePath),
    });

    const { data } = await this.http.post<UploadResponse>("/chat/upload", form, {
      headers: form.getHeaders(),
    });
    return data;
  }

  // ------------------------------------------------------------------ //
  //  Memory / history                                                    //
  // ------------------------------------------------------------------ //

  async getHistory(sessionId: string): Promise<HistoryResponse> {
    const { data } = await this.http.get<HistoryResponse>(
      `/sessions/${sessionId}/history`
    );
    return data;
  }

  async clearSession(sessionId: string): Promise<void> {
    await this.http.delete(`/sessions/${sessionId}`);
  }
}
