def test_eval_history(client):
    # Perform a query with run_eval=True to guarantee log entry
    payload = {
        "question": "What is the memory consumption of CiteMind?",
        "mode": "hybrid",
        "top_k": 2,
        "run_eval": True
    }
    client.post("/api/query", json=payload)

    response = client.get("/api/eval/history")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert data["total_queries"] >= 1
    assert "history" in data
    assert "summary_by_mode" in data
    assert "hybrid" in data["summary_by_mode"]
    assert data["summary_by_mode"]["hybrid"]["count"] >= 1
