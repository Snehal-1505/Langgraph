import pytest
from app.database.repository import ResearchRepository


def test_repository_crud(db):
    # 1. Create session
    session = ResearchRepository.create_session(
        db=db,
        topic="AI Safety Benchmarks",
        scope="Evaluating alignment metrics",
        depth="detailed",
        max_sources=6
    )
    assert session.id is not None
    assert session.topic == "AI Safety Benchmarks"
    assert session.status == "pending"

    # 2. Add task
    task = ResearchRepository.add_task(
        db=db,
        session_id=session.id,
        task_id="task_benchmarks",
        task_description="Gather alignment benchmarks",
        researcher_role="Trends"
    )
    assert task.task_id == "task_benchmarks"

    # 3. Add source
    source = ResearchRepository.add_source(
        db=db,
        session_id=session.id,
        url="https://example.org/alignment",
        title="Alignment Benchmark 2025",
        domain="example.org",
        extracted_evidence="Evaluated 100 frontier models."
    )
    assert source.domain == "example.org"

    # 4. Add finding
    finding = ResearchRepository.add_finding(
        db=db,
        session_id=session.id,
        task_id="task_benchmarks",
        claim="Alignment robustness increased by 18%.",
        evidence_excerpt="Evaluated 100 frontier models.",
        supporting_sources=[source.url]
    )
    assert finding.claim == "Alignment robustness increased by 18%."

    # 5. Create report
    report = ResearchRepository.create_report(
        db=db,
        session_id=session.id,
        title="Report: Alignment Metrics",
        markdown_content="# Report\n## 1. Executive Summary\nSafe findings.",
        executive_summary="Safe findings."
    )
    assert report.title == "Report: Alignment Metrics"

    # 6. Record event
    event = ResearchRepository.record_event(
        db=db,
        session_id=session.id,
        stage="planning",
        event_type="completed",
        message="Planning completed."
    )
    assert event.stage == "planning"

    # 7. Query helpers
    sources = ResearchRepository.get_sources(db, session.id)
    assert len(sources) == 1

    findings = ResearchRepository.get_findings(db, session.id)
    assert len(findings) == 1

    events = ResearchRepository.get_events(db, session.id)
    assert len(events) == 1

    latest_rep = ResearchRepository.get_latest_report(db, session.id)
    assert latest_rep.id == report.id

    # 8. Delete session & verify cascade
    success = ResearchRepository.delete_session(db, session.id)
    assert success is True
    assert ResearchRepository.get_session(db, session.id) is None
    assert len(ResearchRepository.get_sources(db, session.id)) == 0
