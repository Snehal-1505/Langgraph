import asyncio
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.repository import ResearchRepository
from app.database.models import ResearchSession, Source, Finding, Report, WorkflowEvent
from app.api.schemas.research import ResearchCreateRequest
from app.workers.research_worker import run_research_workflow, active_research_tasks

logger = logging.getLogger(__name__)


class ResearchService:
    @staticmethod
    def create_research_job(db: Session, request: ResearchCreateRequest) -> ResearchSession:
        """Create a new research session record and launch the LangGraph workflow in the background."""
        session = ResearchRepository.create_session(
            db=db,
            topic=request.topic,
            scope=request.scope,
            depth=request.depth,
            max_sources=request.max_sources
        )

        # Launch background task if an event loop is running
        try:
            loop = asyncio.get_running_loop()
            logger.info(f"Event loop found: {loop}. Creating background task for session {session.id}")
            task = loop.create_task(
                run_research_workflow(
                    session_id=session.id,
                    topic=request.topic,
                    scope=request.scope,
                    depth=request.depth,
                    max_sources=request.max_sources
                )
            )
            active_research_tasks[session.id] = task
            logger.info(f"Launched background research job {session.id} for topic: {request.topic}")
        except RuntimeError as e:
            logger.error(f"FAILED to get event loop for session {session.id}: {e}", exc_info=True)

        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[ResearchSession]:
        return ResearchRepository.get_session(db, session_id)

    @staticmethod
    def list_sessions(db: Session, skip: int = 0, limit: int = 20) -> List[ResearchSession]:
        return ResearchRepository.list_sessions(db, skip=skip, limit=limit)

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        # Cancel task if active
        if session_id in active_research_tasks:
            task = active_research_tasks[session_id]
            task.cancel()
            active_research_tasks.pop(session_id, None)

        return ResearchRepository.delete_session(db, session_id)

    @staticmethod
    def cancel_job(db: Session, session_id: str) -> Dict[str, str]:
        if session_id in active_research_tasks:
            task = active_research_tasks[session_id]
            task.cancel()
            return {"id": session_id, "status": "cancelled", "message": "Research task cancellation requested."}

        session = ResearchRepository.get_session(db, session_id)
        if session and session.status == "running":
            ResearchRepository.update_session(db, session_id=session_id, status="cancelled", current_stage="cancelled")
            return {"id": session_id, "status": "cancelled", "message": "Marked session as cancelled."}

        return {"id": session_id, "status": session.status if session else "not_found", "message": "Job is not actively running."}

    @staticmethod
    def get_sources(db: Session, session_id: str) -> List[Source]:
        return ResearchRepository.get_sources(db, session_id)

    @staticmethod
    def get_findings(db: Session, session_id: str) -> List[Finding]:
        return ResearchRepository.get_findings(db, session_id)

    @staticmethod
    def get_latest_report(db: Session, session_id: str) -> Optional[Report]:
        return ResearchRepository.get_latest_report(db, session_id)

    @staticmethod
    def get_events(db: Session, session_id: str) -> List[WorkflowEvent]:
        return ResearchRepository.get_events(db, session_id)
