from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class ResearchCreateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, description="The central research question or topic")
    scope: Optional[str] = Field(None, max_length=1000, description="Optional constraints, context, or specific subtopics")
    depth: Literal["quick", "standard", "detailed"] = Field("standard", description="Depth of research")
    max_sources: int = Field(5, ge=1, le=20, description="Maximum number of sources to collect per perspective")


class ResearchSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic: str
    scope: Optional[str] = None
    depth: str
    max_sources: int
    status: str
    current_stage: str
    error_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    url: str
    title: str
    domain: str
    publication_date: Optional[str] = None
    retrieval_timestamp: datetime
    extracted_evidence: Optional[str] = None
    status: str


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    task_id: str
    claim: str
    evidence_excerpt: Optional[str] = None
    supporting_sources: Optional[List[str]] = None
    confidence_notes: Optional[str] = None
    validation_status: str
    created_at: datetime


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    version: int
    title: str
    markdown_content: str
    executive_summary: Optional[str] = None
    review_status: str
    review_feedback: Optional[Dict[str, Any]] = None
    created_at: datetime


class WorkflowEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    stage: str
    event_type: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ResearchSessionDetailResponse(BaseModel):
    session: ResearchSessionResponse
    sources_count: int
    findings_count: int
    has_report: bool
    latest_report: Optional[ReportResponse] = None


class ConfigResponse(BaseModel):
    app_name: str
    app_version: str
    llm_provider: str
    search_provider: str
    default_depth: str
    max_sources_per_task: int


class ProviderStatusResponse(BaseModel):
    llm_provider: str
    configured_model: str
    ollama_status: str  # "ready", "unreachable", "not_installed"
    ollama_base_url: str
    gemini_configured: bool
    groq_configured: bool
    search_provider: str
    tavily_configured: bool
    active_search_status: str


class ResearchCancelResponse(BaseModel):
    id: str
    status: str
    message: str
