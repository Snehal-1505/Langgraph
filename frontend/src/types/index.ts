export type ResearchStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type ResearchDepth = 'quick' | 'standard' | 'detailed';

export interface ResearchSession {
  id: string;
  topic: string;
  scope?: string | null;
  depth: ResearchDepth;
  max_sources: number;
  status: ResearchStatus;
  current_stage: string;
  error_summary?: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface WorkflowEvent {
  session_id: string;
  stage: string;
  event_type: 'info' | 'running' | 'completed' | 'warning' | 'error';
  message: string;
  data?: Record<string, any>;
  timestamp: string;
}

export interface SourceRecord {
  id: string;
  session_id: string;
  url: string;
  title: string;
  domain: string;
  publication_date?: string | null;
  retrieval_timestamp: string;
  extracted_evidence?: string | null;
  status: string;
}

export interface FindingRecord {
  id: string;
  session_id: string;
  task_id: string;
  claim: string;
  evidence_excerpt?: string | null;
  supporting_sources?: string[];
  confidence_notes?: string | null;
  validation_status: string;
  created_at: string;
}

export interface ReportRecord {
  id: string;
  session_id: string;
  version: number;
  title: string;
  markdown_content: string;
  executive_summary?: string | null;
  review_status: 'passed' | 'revised' | 'warning';
  review_feedback?: {
    passed?: boolean;
    issues?: string[];
    missing_sections?: string[];
    citation_problems?: string[];
    recommendations?: string[];
  } | null;
  created_at: string;
}

export interface ProviderStatus {
  llm_provider: string;
  configured_model: string;
  ollama_status: 'ready' | 'unreachable' | 'not_installed';
  ollama_base_url: string;
  gemini_configured: boolean;
  groq_configured: boolean;
  search_provider: string;
  tavily_configured: boolean;
  active_search_status: string;
}

export interface AppConfig {
  app_name: string;
  app_version: string;
  llm_provider: string;
  search_provider: string;
  default_depth: string;
  max_sources_per_task: number;
}
