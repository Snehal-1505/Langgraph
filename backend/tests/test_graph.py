import pytest
from app.graph.state import merge_sources_reducer, merge_findings_reducer, ResearchWorkflowState
from app.graph.routing import route_sufficiency, route_review
from app.database.checkpointing import get_checkpointer


def test_source_deduplication_reducer():
    existing = [
        {"url": "https://example.com/paper1", "title": "Paper 1", "domain": "example.com"},
        {"url": "https://example.com/paper2", "title": "Paper 2", "domain": "example.com"},
    ]
    new_sources = [
        {"url": "https://example.com/paper2", "title": "Duplicate Paper 2", "domain": "example.com"},
        {"url": "https://example.com/paper3", "title": "Paper 3", "domain": "example.com"},
    ]

    merged = merge_sources_reducer(existing, new_sources)
    assert len(merged) == 3
    urls = [s["url"] for s in merged]
    assert urls == ["https://example.com/paper1", "https://example.com/paper2", "https://example.com/paper3"]


def test_findings_reducer_deduplication():
    existing = [
        {"task_id": "task_1", "source_url": "https://example.com/a", "claim": "Finding A claim text"},
    ]
    new_findings = [
        {"task_id": "task_1", "source_url": "https://example.com/a", "claim": "Finding A claim text"},
        {"task_id": "task_2", "source_url": "https://example.com/b", "claim": "Finding B claim text"},
    ]

    merged = merge_findings_reducer(existing, new_findings)
    assert len(merged) == 2


def test_route_sufficiency():
    # 1. Has sufficient real sources
    state_sufficient = {
        "sources": [
            {"url": "https://example.org/1", "title": "S1"},
            {"url": "https://example.org/2", "title": "S2"}
        ],
        "findings": [{"claim": "C1"}, {"claim": "C2"}, {"claim": "C3"}],
        "attempt_count": 1,
        "max_attempts": 2
    }
    assert route_sufficiency(state_sufficient) == "sufficient"

    # 2. Insufficient and attempts remain -> retry
    state_insufficient = {
        "sources": [],
        "findings": [],
        "attempt_count": 1,
        "max_attempts": 2
    }
    assert route_sufficiency(state_insufficient) == "retry_research"

    # 3. Insufficient but max attempts reached -> bounded transition to sufficient
    state_max_attempts = {
        "sources": [],
        "findings": [],
        "attempt_count": 2,
        "max_attempts": 2
    }
    assert route_sufficiency(state_max_attempts) == "sufficient"


def test_route_review():
    # Passed
    state_pass = {
        "review_result": {"passed": True},
        "revision_count": 0,
        "max_revisions": 2
    }
    assert route_review(state_pass) == "passed"

    # Failed and revisions remain -> revise
    state_fail = {
        "review_result": {"passed": False},
        "revision_count": 0,
        "max_revisions": 2
    }
    assert route_review(state_fail) == "revise"

    # Failed but max revisions reached -> force passed
    state_max_rev = {
        "review_result": {"passed": False},
        "revision_count": 2,
        "max_revisions": 2
    }
    assert route_review(state_max_rev) == "passed"


def test_checkpointing_configuration():
    checkpointer = get_checkpointer()
    assert checkpointer is not None
