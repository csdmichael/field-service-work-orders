from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_seeded_work_items_are_listed():
    response = client.get("/api/work-items")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_work_item_round_trip():
    created = client.post("/api/work-items", json={"title": "Inspect pump seal"})
    assert created.status_code == 201
    item_id = created.json()["id"]

    patched = client.patch(f"/api/work-items/{item_id}", json={"status": "complete"})
    assert patched.json()["status"] == "complete"

    assert client.delete(f"/api/work-items/{item_id}").status_code == 204
    assert client.get(f"/api/work-items/{item_id}").status_code == 404
