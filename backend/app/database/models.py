import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Index,
    JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic = Column(String(500), nullable=False)
    scope = Column(Text, nullable=True)
    depth = Column(String(50), default="standard", nullable=False)
    max_sources = Column(Integer, default=5, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed, cancelled
    current_stage = Column(String(100), default="initialization", nullable=False)
    error_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    tasks = relationship("ResearchTask", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="session", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="session", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="session", cascade="all, delete-orphan")
    events = relationship("WorkflowEvent", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_session_status", "status"),
        Index("idx_session_created", "created_at"),
    )


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(String(100), nullable=False)  # e.g., task_1_trends
    task_description = Column(Text, nullable=False)
    researcher_role = Column(String(100), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    attempt_count = Column(Integer, default=1, nullable=False)
    findings_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="tasks")

    __table_args__ = (
        Index("idx_task_session_id", "session_id"),
    )


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(String(500), nullable=False)
    domain = Column(String(200), nullable=False)
    publication_date = Column(String(100), nullable=True)
    retrieval_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    extracted_evidence = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    status = Column(String(50), default="retrieved", nullable=False)  # retrieved, failed, cached

    session = relationship("ResearchSession", back_populates="sources")

    __table_args__ = (
        Index("idx_source_session_id", "session_id"),
        Index("idx_source_domain", "domain"),
    )


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(String(100), nullable=False)
    claim = Column(Text, nullable=False)
    evidence_excerpt = Column(Text, nullable=True)
    supporting_sources = Column(JSON, nullable=True)  # List of URLs or Source IDs
    confidence_notes = Column(Text, nullable=True)
    validation_status = Column(String(50), default="validated", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="findings")

    __table_args__ = (
        Index("idx_finding_session_id", "session_id"),
    )


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    title = Column(String(500), nullable=False)
    markdown_content = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=True)
    review_status = Column(String(50), default="passed", nullable=False)  # passed, revised, warning
    review_feedback = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="reports")

    __table_args__ = (
        Index("idx_report_session_id", "session_id"),
    )


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(100), nullable=False)
    event_type = Column(String(50), default="info", nullable=False)  # info, progress, warning, error, completed
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ResearchSession", back_populates="events")

    __table_args__ = (
        Index("idx_event_session_id", "session_id"),
        Index("idx_event_timestamp", "timestamp"),
    )
