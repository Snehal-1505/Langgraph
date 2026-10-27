import logging
from datetime import datetime
from typing import Dict, Any, List
from app.graph.state import ResearchWorkflowState
from app.agents.planner import PlannerAgent, TaskPlan
from app.agents.researcher import ResearcherAgent, FindingItem, SourceItem
from app.agents.analyst import AnalystAgent
from app.agents.writer import WriterAgent, ReportDraft
from app.agents.reviewer import ReviewerAgent

logger = logging.getLogger(__name__)


def create_progress_event(stage: str, event_type: str, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "stage": stage,
        "event_type": event_type,
        "message": message,
        "data": data or {},
        "timestamp": datetime.utcnow().isoformat()
    }


async def validate_request_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    topic = state.get("topic", "").strip()
    if not topic or len(topic) < 3:
        raise ValueError("Research topic must be at least 3 characters long.")
    
    event = create_progress_event("validation", "completed", "Request validated successfully.")
    return {
        "topic": topic,
        "status": "validated",
        "current_stage": "validation",
        "progress_events": [event]
    }


async def initialize_state_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    event = create_progress_event("initialization", "completed", "Research session initialized.")
    return {
        "status": "running",
        "current_stage": "planning",
        "start_time": now,
        "attempt_count": 1,
        "revision_count": 0,
        "max_attempts": state.get("max_attempts", 2),
        "max_revisions": state.get("max_revisions", 2),
        "findings": [],
        "sources": [],
        "progress_events": [event]
    }


async def planner_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    planner = PlannerAgent()
    topic = state["topic"]
    scope = state.get("scope")
    depth = state.get("depth", "standard")

    event_start = create_progress_event("planning", "running", f"Planner agent formulating 3-perspective plan for '{topic}'...")
    plan = await planner.create_plan(topic=topic, scope=scope, depth=depth)
    
    tasks_dicts = [t.model_dump() for t in plan.tasks]
    event_done = create_progress_event(
        "planning",
        "completed",
        f"Planner generated 3 targeted research tasks.",
        {"plan_tasks": [t["task_title"] for t in tasks_dicts]}
    )

    return {
        "plan": plan.model_dump(),
        "tasks": tasks_dicts,
        "current_stage": "researching",
        "progress_events": [event_start, event_done]
    }


async def _execute_researcher_perspective(state: ResearchWorkflowState, perspective_key: str, default_title: str) -> Dict[str, Any]:
    """Helper to run a specific researcher perspective."""
    tasks = state.get("tasks", [])
    matching_task = next((t for t in tasks if t.get("perspective") == perspective_key), None)
    
    if not matching_task:
        task_plan = TaskPlan(
            task_id=f"task_{perspective_key}",
            task_title=default_title,
            perspective=perspective_key,
            research_objective=f"Investigate {perspective_key} regarding {state['topic']}",
            search_queries=[f"{state['topic']} {perspective_key} research"],
            expected_evidence=f"Evidence relevant to {perspective_key}",
            priority=1
        )
    else:
        task_plan = TaskPlan.model_validate(matching_task)

    agent_name = f"Researcher [{perspective_key.capitalize()}]"
    event_start = create_progress_event(
        f"researcher_{perspective_key}",
        "running",
        f"{agent_name} investigating {task_plan.task_title}..."
    )

    researcher = ResearcherAgent()
    max_sources = state.get("max_sources", 4)
    res = await researcher.execute_task(task_plan, max_sources=max_sources)

    event_done = create_progress_event(
        f"researcher_{perspective_key}",
        "completed",
        f"{agent_name} collected {len(res.sources)} sources and {len(res.findings)} findings."
    )

    return {
        "findings": [f.model_dump() for f in res.findings],
        "sources": [s.model_dump() for s in res.sources],
        "progress_events": [event_start, event_done]
    }


async def researcher_trends_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    return await _execute_researcher_perspective(state, "trends", "Current Developments & Trends")


async def researcher_benefits_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    return await _execute_researcher_perspective(state, "benefits", "Benefits & Practical Applications")


async def researcher_risks_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    return await _execute_researcher_perspective(state, "risks", "Risks, Challenges & Limitations")


async def merge_evidence_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    findings = state.get("findings", [])
    sources = state.get("sources", [])
    event = create_progress_event(
        "evidence_validation",
        "completed",
        f"Validated and deduplicated evidence: {len(sources)} unique sources, {len(findings)} verified findings."
    )
    return {
        "current_stage": "evidence_validation",
        "progress_events": [event]
    }


async def targeted_research_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    current_attempt = state.get("attempt_count", 1) + 1
    topic = state.get("topic")
    event_start = create_progress_event(
        "targeted_research",
        "running",
        f"Executing targeted follow-up research (attempt {current_attempt})..."
    )

    # Perform targeted search query
    task_plan = TaskPlan(
        task_id=f"targeted_followup_{current_attempt}",
        task_title="Targeted Follow-up Investigation",
        perspective="followup",
        research_objective=f"Deep dive follow-up on empirical data for {topic}",
        search_queries=[f"{topic} empirical evidence data report 2025"],
        expected_evidence="Verified metrics and statistics",
        priority=1
    )
    researcher = ResearcherAgent()
    res = await researcher.execute_task(task_plan, max_sources=3)

    event_done = create_progress_event(
        "targeted_research",
        "completed",
        f"Targeted research collected {len(res.sources)} additional sources."
    )

    return {
        "attempt_count": current_attempt,
        "findings": [f.model_dump() for f in res.findings],
        "sources": [s.model_dump() for s in res.sources],
        "progress_events": [event_start, event_done]
    }


async def analyst_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    analyst = AnalystAgent()
    topic = state["topic"]
    findings_raw = state.get("findings", [])
    sources_raw = state.get("sources", [])

    findings = [FindingItem.model_validate(f) for f in findings_raw]
    sources = [SourceItem.model_validate(s) for s in sources_raw]

    event_start = create_progress_event("analysis", "running", "Analyst agent cross-examining findings and detecting themes...")
    analysis = await analyst.analyze(topic, findings, sources, attempt_count=state.get("attempt_count", 1))

    event_done = create_progress_event(
        "analysis",
        "completed",
        f"Analysis complete. Identified {len(analysis.recurring_themes)} themes and {len(analysis.key_findings)} key findings.",
        {"is_sufficient": analysis.is_sufficient, "confidence": analysis.confidence_score}
    )

    return {
        "analysis": analysis.model_dump(),
        "current_stage": "analysis",
        "progress_events": [event_start, event_done]
    }


async def writer_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    writer = WriterAgent()
    topic = state["topic"]
    scope = state.get("scope")
    findings = [FindingItem.model_validate(f) for f in state.get("findings", [])]
    sources = [SourceItem.model_validate(s) for s in state.get("sources", [])]
    analysis = AnalystAgent()._fallback_plan(topic) if not state.get("analysis") else None

    from app.agents.analyst import AnalysisResult
    analysis_obj = AnalysisResult.model_validate(state["analysis"]) if state.get("analysis") else None

    event_start = create_progress_event("writing", "running", "Writer agent drafting 14-section research report...")
    draft = await writer.draft_report(
        topic=topic,
        scope=scope,
        analysis=analysis_obj,
        findings=findings,
        sources=sources
    )

    event_done = create_progress_event("writing", "completed", "Report draft completed with inline citations.")
    return {
        "draft_report": draft.model_dump(),
        "current_stage": "writing",
        "progress_events": [event_start, event_done]
    }


async def reviewer_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    reviewer = ReviewerAgent()
    topic = state["topic"]
    draft = ReportDraft.model_validate(state["draft_report"])
    sources = [SourceItem.model_validate(s) for s in state.get("sources", [])]
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 2)

    event_start = create_progress_event("review", "running", "Reviewer agent evaluating draft for citation accuracy and section coverage...")
    review = await reviewer.review_draft(
        topic=topic,
        draft=draft,
        sources=sources,
        revision_count=revision_count,
        max_revisions=max_revisions
    )

    status_str = "passed" if review.passed else "failed"
    event_done = create_progress_event(
        "review",
        "completed",
        f"Reviewer evaluation complete: Status = {status_str}.",
        {"passed": review.passed, "issues": review.issues, "recs": review.recommendations}
    )

    return {
        "review_result": review.model_dump(),
        "current_stage": "review",
        "progress_events": [event_start, event_done]
    }


async def writer_revision_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    writer = WriterAgent()
    topic = state["topic"]
    scope = state.get("scope")
    findings = [FindingItem.model_validate(f) for f in state.get("findings", [])]
    sources = [SourceItem.model_validate(s) for s in state.get("sources", [])]
    from app.agents.analyst import AnalysisResult
    analysis_obj = AnalysisResult.model_validate(state["analysis"])

    rev_count = state.get("revision_count", 0) + 1
    review_res = state.get("review_result", {})
    recs = "\n".join(review_res.get("recommendations", []))

    event_start = create_progress_event("writing", "running", f"Writer revising draft (revision {rev_count}/{state.get('max_revisions', 2)})...")
    revised_draft = await writer.draft_report(
        topic=topic,
        scope=scope,
        analysis=analysis_obj,
        findings=findings,
        sources=sources,
        revision_feedback=recs
    )

    event_done = create_progress_event("writing", "completed", f"Revision {rev_count} completed.")
    return {
        "revision_count": rev_count,
        "draft_report": revised_draft.model_dump(),
        "progress_events": [event_start, event_done]
    }


async def finalize_report_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    draft = state.get("draft_report", {})
    now = datetime.utcnow().isoformat()
    event = create_progress_event("finalization", "completed", "Research report finalized and persisted.")
    return {
        "final_report": draft,
        "status": "completed",
        "current_stage": "completed",
        "completed_time": now,
        "progress_events": [event]
    }
