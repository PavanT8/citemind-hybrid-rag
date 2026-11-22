def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "provider" in data
    assert data["documents_indexed"] >= 1


def test_load_sample_paper(client):
    response = client.post("/api/documents/load-sample")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample_paper.pdf"
    assert data["page_count"] == 4
    assert data["chunk_count"] > 0
    assert data["is_sample"] is True


def test_list_documents(client):
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(d["filename"] == "sample_paper.pdf" for d in data)


def test_query_modes(client):
    modes = ["hybrid", "dense", "bm25"]
    for mode in modes:
        payload = {
            "question": "What is the mathematical formulation of Reciprocal Rank Fusion?",
            "mode": mode,
            "top_k": 3,
            "run_eval": True
        }
        response = client.post("/api/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["citations"]) > 0
        assert data["metrics"]["mode"] == mode
        assert "retrieval_ms" in data["metrics"]
        assert "generation_ms" in data["metrics"]
        assert "faithfulness" in data["metrics"]
        assert "citation_coverage" in data["metrics"]


def test_invalid_query_validation(client):
    # Invalid mode
    payload = {
        "question": "What is RRF?",
        "mode": "invalid_mode",
        "top_k": 3
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 422
