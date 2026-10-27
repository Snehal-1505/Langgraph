import {
  ResearchSession,
  SourceRecord,
  FindingRecord,
  ReportRecord,
  ProviderStatus,
  AppConfig,
  ResearchDepth
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `HTTP error ${res.status}`;
    try {
      const data = await res.json();
      if (data.detail) errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  async getConfig(): Promise<AppConfig> {
    const res = await fetch(`${API_BASE}/config`);
    return handleResponse<AppConfig>(res);
  },

  async getProviders(): Promise<ProviderStatus> {
    const res = await fetch(`${API_BASE}/providers`);
    return handleResponse<ProviderStatus>(res);
  },

  async createResearch(params: {
    topic: string;
    scope?: string;
    depth?: ResearchDepth;
    max_sources?: number;
  }): Promise<ResearchSession> {
    const res = await fetch(`${API_BASE}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    return handleResponse<ResearchSession>(res);
  },

  async getSession(id: string): Promise<ResearchSession> {
    const res = await fetch(`${API_BASE}/research/${id}`);
    return handleResponse<ResearchSession>(res);
  },

  async listSessions(skip = 0, limit = 20): Promise<ResearchSession[]> {
    const res = await fetch(`${API_BASE}/research?skip=${skip}&limit=${limit}`);
    return handleResponse<ResearchSession[]>(res);
  },

  async deleteSession(id: string): Promise<{ message: string; id: string }> {
    const res = await fetch(`${API_BASE}/research/${id}`, { method: 'DELETE' });
    return handleResponse<{ message: string; id: string }>(res);
  },

  async cancelResearch(id: string): Promise<{ id: string; status: string; message: string }> {
    const res = await fetch(`${API_BASE}/research/${id}/cancel`, { method: 'POST' });
    return handleResponse<{ id: string; status: string; message: string }>(res);
  },

  async getReport(id: string): Promise<ReportRecord> {
    const res = await fetch(`${API_BASE}/research/${id}/report`);
    return handleResponse<ReportRecord>(res);
  },

  async getSources(id: string): Promise<SourceRecord[]> {
    const res = await fetch(`${API_BASE}/research/${id}/sources`);
    return handleResponse<SourceRecord[]>(res);
  },

  async getFindings(id: string): Promise<FindingRecord[]> {
    const res = await fetch(`${API_BASE}/research/${id}/findings`);
    return handleResponse<FindingRecord[]>(res);
  },

  getMarkdownExportUrl(id: string): string {
    return `${API_BASE}/research/${id}/export/markdown`;
  },

  getPdfExportUrl(id: string): string {
    return `${API_BASE}/research/${id}/export/pdf`;
  },

  getEventsUrl(id: string): string {
    return `${API_BASE}/research/${id}/events`;
  }
};
