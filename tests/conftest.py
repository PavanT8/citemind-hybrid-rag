import pytest
from fastapi.testclient import TestClient
from backend.app.main import app, index_sample_paper
from backend.app.services.storage import storage_service
from backend.app.services.hybrid_retriever import hybrid_retriever
from backend.app.services.llm_client import llm_client


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Pre-index sample paper for test suite
    index_sample_paper()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
