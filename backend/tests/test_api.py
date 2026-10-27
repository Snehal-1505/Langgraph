import pytest
from app.database.repository import ResearchRepository


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data


def test_config_endpoint(client):
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert "llm_provider" in data
    assert "search_provider" in data


def test_providers_endpoint(client):
    response = client.get("/api/v1/providers")
    assert response.status_code == 200
    data = response.json()
    assert "ollama_status" in data
    assert "active_search_status" in data


def test_create_research_validation(client):
    # Too short topic (<3 chars)
    response = client.post("/api/v1/research", json={"topic": "ai"})
    assert response.status_code == 422


def test_create_and_manage_research(client, db):
    # Create valid research job
    payload = {
        "topic": "Impact of Generative AI on Developer Velocity",
        "scope": "Enterprise software development",
        "depth": "standard",
        "max_sources": 3
    }
    response = client.post("/api/v1/research", json=payload)
    assert response.status_code == 201
    created = response.json()
    research_id = created["id"]
    assert created["topic"] == payload["topic"]

    # Retrieve status
    get_res = client.get(f"/api/v1/research/{research_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == research_id

    # List sessions
    list_res = client.get("/api/v1/research?skip=0&limit=10")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(i["id"] == research_id for i in items)

    # Cancel session
    cancel_res = client.post(f"/api/v1/research/{research_id}/cancel")
    assert cancel_res.status_code == 200

    # Add a mock report to test exports
    ResearchRepository.create_report(
        db=db,
        session_id=research_id,
        title="Test Report",
        markdown_content="# Test Report\n## 1. Executive Summary\nTesting export features.\n## 12. References\n[1](https://example.com)",
        executive_summary="Testing export features."
    )

    # Test Markdown Export
    md_res = client.get(f"/api/v1/research/{research_id}/export/markdown")
    assert md_res.status_code == 200
    assert "text/markdown" in md_res.headers.get("content-type", "")

    # Test PDF Export
    pdf_res = client.get(f"/api/v1/research/{research_id}/export/pdf")
    assert pdf_res.status_code == 200
    assert "application/pdf" in pdf_res.headers.get("content-type", "")
    assert len(pdf_res.content) > 100

    # Delete session
    del_res = client.delete(f"/api/v1/research/{research_id}")
    assert del_res.status_code == 200

    # Verify 404 after deletion
    del_verify = client.get(f"/api/v1/research/{research_id}")
    assert del_verify.status_code == 404
