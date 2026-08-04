from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_draw_and_read_session():
    created = client.post(
        "/api/lottery/sessions",
        json={"participants": ["张三", "李四"]},
    )

    assert created.status_code == 201
    payload = created.json()
    assert payload["success"] is True
    session_id = payload["data"]["session_id"]

    drawn = client.post(f"/api/lottery/sessions/{session_id}/draw")
    assert drawn.status_code == 200
    assert drawn.json()["data"]["drawn_count"] == 1

    current = client.get(f"/api/lottery/sessions/{session_id}")
    assert current.status_code == 200
    assert current.json()["data"]["remaining_count"] == 1


def test_invalid_session_returns_404():
    response = client.get("/api/lottery/sessions/not-found")

    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "SESSION_NOT_FOUND"
