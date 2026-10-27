from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import (
    ResearchSession,
    ResearchTask,
    Source,
    Finding,
    Report,
    WorkflowEvent,
)


class ResearchRepository:
    @staticmethod
    def create_session(
        db: Session,
        topic: str,
        scope: Optional[str] = None,
        depth: str = "standard",
        max_sources: int = 5,
        session_id: Optional[str] = None
    ) -> ResearchSession:
        kwargs = {
            "topic": topic,
            "scope": scope,
            "depth": depth,
            "max_sources": max_sources,
            "status": "pending",
            "current_stage": "initialization"
        }
        if session_id:
            kwargs["id"] = session_id
        session = ResearchSession(**kwargs)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[ResearchSession]:
        return db.query(ResearchSession).filter(ResearchSession.id == session_id).first()

    @staticmethod
    def list_sessions(db: Session, skip: int = 0, limit: int = 20) -> List[ResearchSession]:
        return (
            db.query(ResearchSession)
            .order_by(desc(ResearchSession.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_session(
        db: Session,
        session_id: str,
        status: Optional[str] = None,
        current_stage: Optional[str] = None,
        error_summary: Optional[str] = None,
        completed_at: Optional[datetime] = None,
    ) -> Optional[ResearchSession]:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if not session:
            return None
        if status is not None:
            session.status = status
        if current_stage is not None:
            session.current_stage = current_stage
        if error_summary is not None:
            session.error_summary = error_summary
        if completed_at is not None:
            session.completed_at = completed_at
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def add_task(
        db: Session,
        session_id: str,
        task_id: str,
        task_description: str,
        researcher_role: str,
        status: str = "pending",
        findings_summary: Optional[str] = None
    ) -> ResearchTask:
        task = ResearchTask(
            session_id=session_id,
            task_id=task_id,
            task_description=task_description,
            researcher_role=researcher_role,
            status=status,
            findings_summary=findings_summary
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def add_source(
        db: Session,
        session_id: str,
        url: str,
        title: str,
        domain: str,
        publication_date: Optional[str] = None,
        extracted_evidence: Optional[str] = None,
        status: str = "retrieved",
        content_hash: Optional[str] = None
    ) -> Source:
        source = Source(
            session_id=session_id,
            url=url,
            title=title,
            domain=domain,
            publication_date=publication_date,
            extracted_evidence=extracted_evidence,
            status=status,
            content_hash=content_hash
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def get_sources(db: Session, session_id: str) -> List[Source]:
        return db.query(Source).filter(Source.session_id == session_id).all()

    @staticmethod
    def add_finding(
        db: Session,
        session_id: str,
        task_id: str,
        claim: str,
        evidence_excerpt: Optional[str] = None,
        supporting_sources: Optional[List[str]] = None,
        confidence_notes: Optional[str] = None,
        validation_status: str = "validated"
    ) -> Finding:
        finding = Finding(
            session_id=session_id,
            task_id=task_id,
            claim=claim,
            evidence_excerpt=evidence_excerpt,
            supporting_sources=supporting_sources or [],
            confidence_notes=confidence_notes,
            validation_status=validation_status
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        return finding

    @staticmethod
    def get_findings(db: Session, session_id: str) -> List[Finding]:
        return db.query(Finding).filter(Finding.session_id == session_id).all()

    @staticmethod
    def create_report(
        db: Session,
        session_id: str,
        title: str,
        markdown_content: str,
        executive_summary: Optional[str] = None,
        review_status: str = "passed",
        review_feedback: Optional[Dict[str, Any]] = None,
        version: int = 1
    ) -> Report:
        report = Report(
            session_id=session_id,
            title=title,
            markdown_content=markdown_content,
            executive_summary=executive_summary,
            review_status=review_status,
            review_feedback=review_feedback,
            version=version
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_latest_report(db: Session, session_id: str) -> Optional[Report]:
        return (
            db.query(Report)
            .filter(Report.session_id == session_id)
            .order_by(desc(Report.version))
            .first()
        )

    @staticmethod
    def record_event(
        db: Session,
        session_id: str,
        stage: str,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> WorkflowEvent:
        event = WorkflowEvent(
            session_id=session_id,
            stage=stage,
            event_type=event_type,
            message=message,
            data=data
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_events(db: Session, session_id: str) -> List[WorkflowEvent]:
        return (
            db.query(WorkflowEvent)
            .filter(WorkflowEvent.session_id == session_id)
            .order_by(WorkflowEvent.timestamp)
            .all()
        )
