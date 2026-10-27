import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime


def merge_sources_reducer(existing: List[Dict[str, Any]], new_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Reducer that merges and deduplicates sources based on URL."""
    if not existing:
        existing = []
    if not new_sources:
        return existing

    seen_urls = {s.get("url") for s in existing if s.get("url")}
    merged = list(existing)

    for src in new_sources:
        url = src.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            merged.append(src)

    return merged


def merge_findings_reducer(existing: List[Dict[str, Any]], new_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Reducer that merges findings, deduplicating substantially similar claims."""
    if not existing:
        existing = []
    if not new_findings:
        return existing

    seen_keys = {(f.get("task_id", ""), f.get("source_url", ""), f.get("claim", "")[:50]) for f in existing}
    merged = list(existing)

    for item in new_findings:
        key = (item.get("task_id", ""), item.get("source_url", ""), item.get("claim", "")[:50])
        if key not in seen_keys:
            seen_keys.add(key)
            merged.append(item)

    return merged


class ResearchWorkflowState(TypedDict, total=False):
    # Identifiers & Parameters
    research_id: str
    topic: str
    scope: Optional[str]
    depth: str
    max_sources: int

    # Workflow Planning & Tasks
    plan: Optional[Dict[str, Any]]
    tasks: List[Dict[str, Any]]

    # Parallel & Merged Evidence
    findings: Annotated[List[Dict[str, Any]], merge_findings_reducer]
    sources: Annotated[List[Dict[str, Any]], merge_sources_reducer]

    # Analysis & Synthesis
    analysis: Optional[Dict[str, Any]]
    draft_report: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]

    # Review & Revisions
    review_result: Optional[Dict[str, Any]]
    attempt_count: int
    revision_count: int
    max_attempts: int
    max_revisions: int

    # Status & Progress
    status: str
    current_stage: str
    error: Optional[str]
    start_time: str
    completed_time: Optional[str]
    progress_events: Annotated[List[Dict[str, Any]], operator.add]
