import logging
from langgraph.graph import StateGraph, START, END
from app.graph.state import ResearchWorkflowState
from app.graph.nodes import (
    validate_request_node,
    initialize_state_node,
    planner_node,
    researcher_trends_node,
    researcher_benefits_node,
    researcher_risks_node,
    merge_evidence_node,
    targeted_research_node,
    analyst_node,
    writer_node,
    reviewer_node,
    writer_revision_node,
    finalize_report_node,
)
from app.graph.routing import route_sufficiency, route_review
from app.database.checkpointing import get_checkpointer

logger = logging.getLogger(__name__)


def build_research_graph():
    """
    Constructs and compiles the complete multi-agent research LangGraph workflow.
    Features:
    - Parallel 3-perspective researchers
    - Reducer-based evidence merging and deduplication
    - Bounded sufficiency check and targeted follow-up research
    - Analyst cross-examination
    - Writer drafting complete 14-section report
    - Reviewer validation with bounded revision loop
    - Persisted checkpointing
    """
    workflow = StateGraph(ResearchWorkflowState)

    # 1. Register Nodes
    workflow.add_node("validate_request", validate_request_node)
    workflow.add_node("initialize_state", initialize_state_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher_trends", researcher_trends_node)
    workflow.add_node("researcher_benefits", researcher_benefits_node)
    workflow.add_node("researcher_risks", researcher_risks_node)
    workflow.add_node("merge_evidence", merge_evidence_node)
    workflow.add_node("targeted_research", targeted_research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("writer_revision", writer_revision_node)
    workflow.add_node("finalize_report", finalize_report_node)

    # 2. Sequential & Parallel Edges
    workflow.add_edge(START, "validate_request")
    workflow.add_edge("validate_request", "initialize_state")
    workflow.add_edge("initialize_state", "planner")

    # Parallel Fan-out from Planner to 3 Researchers
    workflow.add_edge("planner", "researcher_trends")
    workflow.add_edge("planner", "researcher_benefits")
    workflow.add_edge("planner", "researcher_risks")

    # Parallel Fan-in converging into merge_evidence
    workflow.add_edge("researcher_trends", "merge_evidence")
    workflow.add_edge("researcher_benefits", "merge_evidence")
    workflow.add_edge("researcher_risks", "merge_evidence")

    # Conditional Routing on Sufficiency
    workflow.add_conditional_edges(
        "merge_evidence",
        route_sufficiency,
        {
            "retry_research": "targeted_research",
            "sufficient": "analyst"
        }
    )
    workflow.add_edge("targeted_research", "merge_evidence")

    # Synthesis Pipeline
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "reviewer")

    # Conditional Routing on Review Pass / Revise
    workflow.add_conditional_edges(
        "reviewer",
        route_review,
        {
            "revise": "writer_revision",
            "passed": "finalize_report"
        }
    )
    workflow.add_edge("writer_revision", "reviewer")

    # Finalization to END
    workflow.add_edge("finalize_report", END)

    # Compile with checkpointer
    checkpointer = get_checkpointer()
    compiled_app = workflow.compile(checkpointer=checkpointer)
    return compiled_app


# Singleton compiled graph instance
research_graph = build_research_graph()
