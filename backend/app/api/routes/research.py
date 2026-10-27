import asyncio
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from app.database.session import get_db
from app.services.research_service import ResearchService
from app.services.event_broadcaster import event_broadcaster
from app.services.pdf_exporter import PDFExporter
from app.api.schemas.research import (
    ResearchCreateRequest,
    ResearchSessionResponse,
    SourceResponse,
    FindingResponse,
    ReportResponse,
    WorkflowEventResponse,
    ResearchCancelResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["Research"])


@router.post("", response_model=ResearchSessionResponse, status_code=201)
async def create_research(request: ResearchCreateRequest, db: Session = Depends(get_db)):
    """Create a new research session and initiate workflow execution in the background."""
    session = ResearchService.create_research_job(db, request)
    return session


@router.get("", response_model=List[ResearchSessionResponse])
def list_research_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List research history with pagination."""
    return ResearchService.list_sessions(db, skip=skip, limit=limit)


@router.get("/{research_id}", response_model=ResearchSessionResponse)
def get_research_session(research_id: str, db: Session = Depends(get_db)):
    """Get research session status and metadata."""
    session = ResearchService.get_session(db, research_id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")
    return session


@router.get("/{research_id}/events")
async def stream_research_events(research_id: str, db: Session = Depends(get_db)):
    """Stream real-time research progress updates through Server-Sent Events (SSE)."""
    session = ResearchService.get_session(db, research_id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")

    async def event_generator():
        # First send any previously recorded events to sync client state
        historical_events = ResearchService.get_events(db, research_id)
        for ev in historical_events:
            yield {
                "event": "workflow_event",
                "data": json.dumps({
                    "session_id": ev.session_id,
                    "stage": ev.stage,
                    "event_type": ev.event_type,
                    "message": ev.message,
                    "data": ev.data,
                    "timestamp": ev.timestamp.isoformat()
                })
            }

        # If already completed or failed, close stream
        if session.status in ("completed", "failed", "cancelled"):
            yield {
                "event": "workflow_event",
                "data": json.dumps({
                    "session_id": session.id,
                    "stage": session.current_stage,
                    "event_type": session.status,
                    "message": f"Research session is {session.status}.",
                    "timestamp": session.updated_at.isoformat()
                })
            }
            return

        # Subscribe to live events queue
        queue = await event_broadcaster.subscribe(research_id)
        try:
            while True:
                # Wait for next event with a periodic heartbeat ping
                try:
                    event_payload = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield {"event": "workflow_event", "data": event_payload}
                    data_dict = json.loads(event_payload)
                    if data_dict.get("event_type") in ("completed", "failed", "cancelled"):
                        break
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keep-alive"}
        finally:
            await event_broadcaster.unsubscribe(research_id, queue)

    return EventSourceResponse(event_generator())


@router.get("/{research_id}/report", response_model=ReportResponse)
def get_research_report(research_id: str, db: Session = Depends(get_db)):
    """Retrieve the generated research report for a session."""
    report = ResearchService.get_latest_report(db, research_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or not yet generated.")
    return report


@router.get("/{research_id}/sources", response_model=List[SourceResponse])
def get_research_sources(research_id: str, db: Session = Depends(get_db)):
    """Retrieve collected web sources and evidence passages."""
    return ResearchService.get_sources(db, research_id)


@router.get("/{research_id}/findings", response_model=List[FindingResponse])
def get_research_findings(research_id: str, db: Session = Depends(get_db)):
    """Retrieve synthesized structured findings for a session."""
    return ResearchService.get_findings(db, research_id)


@router.delete("/{research_id}")
def delete_research_session(research_id: str, db: Session = Depends(get_db)):
    """Delete a research session and all associated database records."""
    success = ResearchService.delete_session(db, research_id)
    if not success:
        raise HTTPException(status_code=404, detail="Research session not found")
    return {"message": "Session deleted successfully", "id": research_id}


@router.post("/{research_id}/cancel", response_model=ResearchCancelResponse)
def cancel_research(research_id: str, db: Session = Depends(get_db)):
    """Cancel a running research workflow job."""
    result = ResearchService.cancel_job(db, research_id)
    return ResearchCancelResponse(
        id=result["id"],
        status=result["status"],
        message=result["message"]
    )


@router.get("/{research_id}/export/markdown")
def export_report_markdown(research_id: str, db: Session = Depends(get_db)):
    """Export the report as a downloadable Markdown file."""
    report = ResearchService.get_latest_report(db, research_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready for export.")

    filename = f"research_report_{research_id[:8]}.md"
    return Response(
        content=report.markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{research_id}/export/pdf")
def export_report_pdf(research_id: str, db: Session = Depends(get_db)):
    """Export the report as a downloadable PDF document."""
    report = ResearchService.get_latest_report(db, research_id)
    session = ResearchService.get_session(db, research_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready for export.")

    pdf_buffer = PDFExporter.generate_pdf(
        title=report.title,
        markdown_content=report.markdown_content,
        metadata={
            "status": session.status if session else "Completed",
            "date": report.created_at.strftime("%Y-%m-%d %H:%M UTC")
        }
    )

    filename = f"research_report_{research_id[:8]}.pdf"
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
