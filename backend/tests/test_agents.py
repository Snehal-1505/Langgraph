import pytest
from app.agents.planner import PlannerAgent, ResearchPlan
from app.agents.researcher import ResearcherAgent, TaskPlan, FindingItem, SourceItem
from app.agents.analyst import AnalystAgent, AnalysisResult
from app.agents.writer import WriterAgent, ReportDraft
from app.agents.reviewer import ReviewerAgent, ReviewResult


@pytest.mark.asyncio
async def test_planner_output_schema():
    planner = PlannerAgent()
    plan = await planner.create_plan(
        topic="Impact of Generative AI on software engineering",
        scope="Focus on code generation and developer productivity",
        depth="standard"
    )

    assert isinstance(plan, ResearchPlan)
    assert len(plan.tasks) == 3
    perspectives = {t.perspective for t in plan.tasks}
    assert perspectives == {"trends", "benefits", "risks"}
    for t in plan.tasks:
        assert len(t.search_queries) >= 1
        assert t.research_objective


@pytest.mark.asyncio
async def test_researcher_output_schema():
    researcher = ResearcherAgent()
    task = TaskPlan(
        task_id="task_trends",
        task_title="Trends in Generative AI",
        perspective="trends",
        research_objective="Evaluate adoption metrics",
        search_queries=["generative ai developer adoption 2024"],
        expected_evidence="Adoption statistics",
        priority=1
    )

    result = await researcher.execute_task(task, max_sources=2)
    assert result.task_id == "task_trends"
    assert result.perspective == "trends"
    assert len(result.findings) > 0
    assert result.findings[0].claim
    assert result.findings[0].source_url


@pytest.mark.asyncio
async def test_analyst_agent_evaluation():
    analyst = AnalystAgent()
    findings = [
        FindingItem(
            task_id="task_trends",
            claim="Adoption reached 60% across enterprise teams.",
            source_title="Tech Survey",
            source_url="https://example.org/survey",
            domain="example.org",
            evidence_passage="60% of surveyed engineering organizations adopted coding assistants.",
            relevance_explanation="Direct empirical metric"
        ),
        FindingItem(
            task_id="task_risks",
            claim="Security flaws were detected in 15% of generated snippets.",
            source_title="Security Audit",
            source_url="https://example.edu/audit",
            domain="example.edu",
            evidence_passage="Static analysis revealed vulnerabilities in 15% of synthetic code outputs.",
            relevance_explanation="Crucial security risk factor"
        )
    ]
    sources = [
        SourceItem(
            url="https://example.org/survey",
            title="Tech Survey",
            domain="example.org",
            extracted_evidence="60% adoption"
        ),
        SourceItem(
            url="https://example.edu/audit",
            title="Security Audit",
            domain="example.edu",
            extracted_evidence="15% vulnerabilities"
        )
    ]

    analysis = await analyst.analyze("Generative AI Software Development", findings, sources, attempt_count=1)
    assert isinstance(analysis, AnalysisResult)
    assert len(analysis.key_findings) > 0
    assert len(analysis.recurring_themes) > 0
    assert analysis.is_sufficient is True


@pytest.mark.asyncio
async def test_writer_and_reviewer_flow():
    writer = WriterAgent()
    reviewer = ReviewerAgent()

    sources = [
        SourceItem(
            url="https://example.org/study-1",
            title="Productivity Benchmark",
            domain="example.org",
            extracted_evidence="Developer task completion time decreased by 25%."
        )
    ]
    findings = [
        FindingItem(
            task_id="task_benefits",
            claim="25% decrease in developer task completion time.",
            source_title="Productivity Benchmark",
            source_url="https://example.org/study-1",
            domain="example.org",
            evidence_passage="Developer task completion time decreased by 25%."
        )
    ]
    analysis = AnalysisResult(
        key_findings=["Productivity accelerated by 25%."],
        recurring_themes=["Operational Velocity"],
        conflicting_evidence=[],
        evidence_gaps=[],
        confidence_score=0.9,
        confidence_explanation="Supported by empirical benchmark",
        is_sufficient=True,
        remaining_questions=[]
    )

    draft = await writer.draft_report("GenAI Productivity", None, analysis, findings, sources)
    assert isinstance(draft, ReportDraft)
    assert "Executive Summary" in draft.markdown_content
    assert "Methodology" in draft.markdown_content
    assert "Key Findings" in draft.markdown_content
    assert "References" in draft.markdown_content
    assert "Limitations" in draft.markdown_content

    # Reviewer evaluation
    review = await reviewer.review_draft("GenAI Productivity", draft, sources, revision_count=0, max_revisions=2)
    assert isinstance(review, ReviewResult)
    assert review.passed is True


@pytest.mark.asyncio
async def test_reviewer_bounded_revision_limit():
    reviewer = ReviewerAgent()
    # A deliberately flawed draft missing mandatory sections
    broken_draft = ReportDraft(
        title="Incomplete",
        executive_summary="Short",
        markdown_content="Just a few lines without required headers."
    )

    # Initial check fails
    initial_review = await reviewer.review_draft("Topic", broken_draft, [], revision_count=0, max_revisions=2)
    assert initial_review.passed is False
    assert len(initial_review.missing_sections) > 0

    # At revision limit (revision_count=2, max_revisions=2), must force pass with warning
    bounded_review = await reviewer.review_draft("Topic", broken_draft, [], revision_count=2, max_revisions=2)
    assert bounded_review.passed is True
    assert any("warning" in str(iss).lower() or "limit" in str(iss).lower() for iss in bounded_review.issues)
