import logging
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from app.tools.llm_provider import get_llm
from app.agents.writer import ReportDraft
from app.agents.researcher import SourceItem

logger = logging.getLogger(__name__)


class ReviewResult(BaseModel):
    passed: bool = Field(..., description="True if report meets research quality and citation standards")
    issues: List[str] = Field(default_factory=list, description="General quality or coverage issues identified")
    unsupported_claims: List[str] = Field(default_factory=list, description="Claims made without reasonable source backing")
    missing_sections: List[str] = Field(default_factory=list, description="Expected sections that were omitted")
    citation_problems: List[str] = Field(default_factory=list, description="Citations with invalid numbers or fabricated URLs")
    recommendations: List[str] = Field(default_factory=list, description="Concrete revision recommendations for the Writer")


REVIEWER_SYSTEM_PROMPT = """You are the Senior Research Quality Reviewer for ResearchLab AI.
Your purpose is to rigorously inspect draft research reports for factual grounding, section completeness, and citation integrity.

CRITICAL CHECKS:
1. Completeness: Does the report cover trends, benefits, and risks?
2. Integrity: Are citations [1], [2] properly grounded in the provided sources list?
3. Neutrality: Does it acknowledge uncertainties and counter-arguments?
4. Format: Are required sections (Executive Summary, Findings, References, Limitations) present?

If the draft is acceptable, return passed=True with empty issues.
If critical sections are missing or citations point to non-existent sources, return passed=False with explicit recommendations.
"""

REQUIRED_HEADERS = [
    "executive summary",
    "methodology",
    "key findings",
    "detailed analysis",
    "benefits",
    "risks",
    "references",
    "limitations"
]


class ReviewerAgent:
    def __init__(self, llm=None):
        self.llm = llm or get_llm(temperature=0.1)

    async def review_draft(
        self,
        topic: str,
        draft: ReportDraft,
        sources: List[SourceItem],
        revision_count: int = 0,
        max_revisions: int = 2
    ) -> ReviewResult:
        """
        Perform deterministic checks + LLM-based review.
        If revision_count >= max_revisions, bounded logic forces passed=True with warnings to prevent infinite loop.
        """
        # 1. Deterministic validation checks
        deterministic_issues = []
        missing_sections = []
        citation_problems = []

        content_lower = draft.markdown_content.lower()

        # Check required sections
        for header in REQUIRED_HEADERS:
            if header not in content_lower:
                missing_sections.append(f"Missing section or header for '{header}'")

        # Check citation numbers vs available sources
        citation_matches = re.findall(r"\[(\d+)\]", draft.markdown_content)
        citation_numbers = [int(m) for m in citation_matches if m.isdigit()]

        max_valid_index = len(sources)
        if sources:
            for num in citation_numbers:
                if num < 1 or num > max_valid_index:
                    citation_problems.append(f"Citation [{num}] is out of bounds (only {max_valid_index} sources available).")
        elif citation_numbers:
            citation_problems.append("Report cites sources when zero external sources were successfully retrieved.")

        # Minimum length check
        if len(draft.markdown_content) < 400:
            deterministic_issues.append("Report is overly brief and lacks detailed substantive analysis.")

        # 2. Check if maximum revisions reached
        if revision_count >= max_revisions:
            logger.info(f"Max revisions ({max_revisions}) reached. Forcing pass with quality warning.")
            return ReviewResult(
                passed=True,
                issues=deterministic_issues + [f"Report approved at revision limit ({max_revisions}) with quality advisory."],
                unsupported_claims=[],
                missing_sections=missing_sections,
                citation_problems=citation_problems,
                recommendations=["Report finalized under bounded revision threshold."]
            )

        # 3. LLM Review if deterministic checks don't immediately fail with egregious omissions
        prompt = (
            f"Topic: {topic}\n"
            f"Total Sources Collected: {len(sources)}\n"
            f"Draft Title: {draft.title}\n"
            f"Draft Excerpt (first 1500 chars):\n{draft.markdown_content[:1500]}\n\n"
            f"Deterministic Missing Sections: {missing_sections}\n"
            f"Deterministic Citation Problems: {citation_problems}\n"
        )

        try:
            if hasattr(self.llm, "with_structured_output"):
                structured = self.llm.with_structured_output(ReviewResult)
                res = await structured.ainvoke([
                    SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
                    HumanMessage(content=prompt)
                ])
                if isinstance(res, ReviewResult):
                    # Combine deterministic findings
                    res.missing_sections = list(set(res.missing_sections + missing_sections))
                    res.citation_problems = list(set(res.citation_problems + citation_problems))
                    if missing_sections or citation_problems:
                        res.passed = False
                    return res
        except Exception as e:
            logger.warning(f"Structured review call failed: {e}. Using deterministic review.")

        # Deterministic outcome
        passed = (len(missing_sections) == 0 and len(citation_problems) == 0)
        recs = []
        if missing_sections:
            recs.append("Ensure all 14 mandatory report sections are clearly delineated.")
        if citation_problems:
            recs.append("Verify all inline brackets match the indexed source references.")

        return ReviewResult(
            passed=passed,
            issues=deterministic_issues,
            unsupported_claims=[],
            missing_sections=missing_sections,
            citation_problems=citation_problems,
            recommendations=recs or ["Report meets standard research presentation criteria."]
        )
