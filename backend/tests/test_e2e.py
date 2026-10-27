import pytest
from app.graph.builder import research_graph


@pytest.mark.asyncio
async def test_full_workflow_end_to_end():
    """
    Test the full multi-agent LangGraph workflow end-to-end
    using deterministic mock tools to verify state transitions and output completeness.
    """
    session_id = "test_e2e_session_123"
    initial_state = {
        "research_id": session_id,
        "topic": "Evaluating LLM Test Generation in Mission-Critical Systems",
        "scope": "Aerospace and Automotive embedded testing",
        "depth": "standard",
        "max_sources": 3,
        "max_attempts": 2,
        "max_revisions": 2
    }

    config = {"configurable": {"thread_id": session_id}}

    final_state = {}
    async for output in research_graph.astream(initial_state, config=config, stream_mode="updates"):
        for _, update in output.items():
            if isinstance(update, dict):
                final_state.update(update)

    # Assertions
    assert final_state.get("status") == "completed"
    assert final_state.get("current_stage") == "completed"
    assert final_state.get("completed_time") is not None

    # Check that plan was created
    assert "plan" in final_state or final_state.get("tasks")

    # Check that sources and findings were collected and merged
    assert "sources" in final_state
    assert "findings" in final_state

    # Check that report draft exists with required sections
    final_report = final_state.get("final_report") or final_state.get("draft_report")
    assert final_report is not None
    assert "markdown_content" in final_report
    content = final_report["markdown_content"]
    assert "Executive Summary" in content
    assert "Key Findings" in content
    assert "References" in content
    assert "Limitations" in content
