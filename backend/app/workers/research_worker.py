import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.graph.builder import research_graph
from app.database.session import SessionLocal
from app.database.repository import ResearchRepository
from app.services.event_broadcaster import event_broadcaster

logger = logging.getLogger(__name__)

# Registry of active asyncio tasks for cancellation support
active_research_tasks: Dict[str, asyncio.Task] = {}


async def run_research_workflow(
    session_id: str,
    topic: str,
    scope: Optional[str] = None,
    depth: str = "standard",
    max_sources: int = 5
):
    """
    Background worker that runs the LangGraph research workflow.
    Streams real-time progress events to SSE and persists state to the database.
    """
    db = SessionLocal()
    try:
        # Mark session as running
        ResearchRepository.update_session(
            db,
            session_id=session_id,
            status="running",
            current_stage="planning"
        )

        initial_state = {
            "research_id": session_id,
            "topic": topic,
            "scope": scope,
            "depth": depth,
            "max_sources": max_sources,
            "max_attempts": 2,
            "max_revisions": 2
        }

        config = {"configurable": {"thread_id": session_id}}

        logger.info(f"Starting research execution for session {session_id}")

        # Stream graph execution node by node
        final_state = {}
        async for output in research_graph.astream(initial_state, config=config, stream_mode="updates"):
            # Check for cancellation
            current_task = asyncio.current_task()
            if current_task and current_task.cancelled():
                raise asyncio.CancelledError()

            for node_name, node_update in output.items():
                if not isinstance(node_update, dict):
                    continue

                # Accumulate latest state
                final_state.update(node_update)

                # Process any progress events emitted by the node
                events = node_update.get("progress_events", [])
                for ev in events:
                    stage = ev.get("stage", node_name)
                    msg = ev.get("message", "")
                    ev_type = ev.get("event_type", "info")
                    data = ev.get("data", {})

                    # 1. Persist event to DB
                    ResearchRepository.record_event(
                        db=db,
                        session_id=session_id,
                        stage=stage,
                        event_type=ev_type,
                        message=msg,
                        data=data
                    )

                    # 2. Broadcast live event via SSE
                    await event_broadcaster.broadcast(session_id, {
                        "session_id": session_id,
                        "stage": stage,
                        "event_type": ev_type,
                        "message": msg,
                        "data": data,
                        "timestamp": ev.get("timestamp", datetime.utcnow().isoformat())
                    })

                # Update current stage in DB
                stage_name = node_update.get("current_stage") or node_name
                ResearchRepository.update_session(db, session_id=session_id, current_stage=stage_name)

        # Persist final findings and sources to database
        sources_data = final_state.get("sources", [])
        for s in sources_data:
            ResearchRepository.add_source(
                db=db,
                session_id=session_id,
                url=s.get("url", ""),
                title=s.get("title", ""),
                domain=s.get("domain", ""),
                publication_date=s.get("publication_date"),
                extracted_evidence=s.get("extracted_evidence", ""),
                status=s.get("status", "retrieved")
            )

        findings_data = final_state.get("findings", [])
        for f in findings_data:
            ResearchRepository.add_finding(
                db=db,
                session_id=session_id,
                task_id=f.get("task_id", ""),
                claim=f.get("claim", ""),
                evidence_excerpt=f.get("evidence_passage", ""),
                supporting_sources=[f.get("source_url", "")],
                confidence_notes=f.get("relevance_explanation")
            )

        # Persist Report
        report_data = final_state.get("final_report") or final_state.get("draft_report", {})
        review_data = final_state.get("review_result", {})
        review_status = "passed" if review_data.get("passed") else "warning"

        if report_data:
            ResearchRepository.create_report(
                db=db,
                session_id=session_id,
                title=report_data.get("title", f"Report: {topic}"),
                markdown_content=report_data.get("markdown_content", ""),
                executive_summary=report_data.get("executive_summary", ""),
                review_status=review_status,
                review_feedback=review_data,
                version=1
            )

        # Mark session completed
        ResearchRepository.update_session(
            db=db,
            session_id=session_id,
            status="completed",
            current_stage="completed",
            completed_at=datetime.utcnow()
        )

        # Broadcast completion event
        await event_broadcaster.broadcast(session_id, {
            "session_id": session_id,
            "stage": "completed",
            "event_type": "completed",
            "message": "Research workflow completed successfully.",
            "data": {"report_ready": True},
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"Research session {session_id} completed successfully.")

    except asyncio.CancelledError:
        logger.info(f"Research session {session_id} was cancelled.")
        ResearchRepository.update_session(
            db=db,
            session_id=session_id,
            status="cancelled",
            current_stage="cancelled",
            error_summary="Research cancelled by user."
        )
        await event_broadcaster.broadcast(session_id, {
            "session_id": session_id,
            "stage": "cancelled",
            "event_type": "error",
            "message": "Research job was cancelled.",
            "data": {},
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in research session {session_id}: {str(e)}", exc_info=True)
        ResearchRepository.update_session(
            db=db,
            session_id=session_id,
            status="failed",
            current_stage="failed",
            error_summary=str(e),
            completed_at=datetime.utcnow()
        )
        await event_broadcaster.broadcast(session_id, {
            "session_id": session_id,
            "stage": "failed",
            "event_type": "error",
            "message": f"Workflow failed: {str(e)}",
            "data": {"error": str(e)},
            "timestamp": datetime.utcnow().isoformat()
        })

    finally:
        db.close()
        active_research_tasks.pop(session_id, None)
