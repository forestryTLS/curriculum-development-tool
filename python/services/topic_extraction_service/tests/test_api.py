from fastapi.testclient import TestClient
from app.api.routes import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_non_post_request_extract():
    response = client.get("/extract")
    assert response.status_code == 405


def test_missing_post_body_extract():
    response = client.post("/extract")
    assert response.status_code == 422


def test_invalid_data_type_post_body_extract():
    body = {"pages": "not-a-list"}
    response = client.post("/extract", json=body)
    assert response.status_code == 422


def test_extract_returns_topics():
    body = {
        "pages": [
            {
                "page_number": 1,
                "content": (
                    "Photosynthesis is the process by which green plants convert "
                    "sunlight into chemical energy. Forest ecosystems depend on "
                    "photosynthesis to sustain plant growth and carbon storage."
                ),
            }
        ]
    }
    response = client.post("/extract", json=body)
    assert response.status_code == 200
    data = response.json()
    assert len(data["topics"]) > 0
    assert all("topic" in t and "score" in t for t in data["topics"])
