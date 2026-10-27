import logging
from typing import Literal
from app.graph.state import ResearchWorkflowState

logger = logging.getLogger(__name__)


def route_sufficiency(state: ResearchWorkflowState) -> Literal["sufficient", "retry_research"]:
    """
    Evaluate if gathered evidence is sufficient to proceed to Analyst,
    or if targeted follow-up research is required.
    Bounded by max_attempts.
    """
    sources = state.get("sources", [])
    findings = state.get("findings", [])
    attempt = state.get("attempt_count", 1)
    max_attempts = state.get("max_attempts", 2)

    # Filter out empty or offline placeholder sources
    real_sources = [s for s in sources if "offline.local" not in s.get("url", "")]

    # If we have at least 2 real sources, evidence is sufficient
    if len(real_sources) >= 2 or len(findings) >= 3:
        logger.info(f"Evidence sufficient ({len(real_sources)} sources, {len(findings)} findings). Routing to Analyst.")
        return "sufficient"

    # If insufficient and attempts remain, execute targeted follow-up research
    if attempt < max_attempts:
        logger.info(f"Evidence insufficient ({len(real_sources)} sources). Attempt {attempt}/{max_attempts}. Routing to targeted research.")
        return "retry_research"

    # Otherwise, bound reached; proceed with limited evidence
    logger.info(f"Max research attempts reached ({attempt}/{max_attempts}). Routing to Analyst with limited evidence.")
    return "sufficient"


def route_review(state: ResearchWorkflowState) -> Literal["passed", "revise"]:
    """
    Check if the reviewer approved the report, or if a revision loop is required.
    Bounded by max_revisions.
    """
    review = state.get("review_result", {})
    passed = review.get("passed", False)
    revisions = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 2)

    if passed:
        logger.info("Report passed review. Routing to Finalize.")
        return "passed"

    if revisions < max_revisions:
        logger.info(f"Report failed review. Revision {revisions + 1}/{max_revisions}. Routing to Writer Revision.")
        return "revise"

    logger.info(f"Max revisions reached ({revisions}/{max_revisions}). Finalizing best available draft with warning.")
    return "passed"
