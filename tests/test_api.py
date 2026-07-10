import os
from pathlib import Path

TEST_DB = Path("data/test_tiny_museum.db")
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def sample_object():
    return {
        "name": "Concert Wristband",
        "story": "A paper wristband from a tiny venue and an unexpectedly perfect evening.",
        "room": "Memory box",
        "material": "Paper",
        "mood": "Joyful",
        "color": "Orange",
        "acquired_year": 2024,
        "estimated_age": 2,
        "significance": 4,
        "favorite": False,
    }


def test_health():
    with client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_object_lifecycle():
    with client:
        created = client.post("/api/objects", json=sample_object())
        assert created.status_code == 201
        object_id = created.json()["id"]

        listed = client.get("/api/objects")
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        favorite = client.patch(
            f"/api/objects/{object_id}/favorite", json={"favorite": True}
        )
        assert favorite.status_code == 200
        assert favorite.json()["favorite"] is True

        stats = client.get("/api/stats")
        assert stats.status_code == 200
        assert stats.json()["total"] == 1

        exhibit = client.post(
            "/api/exhibitions/generate", json={"theme": "joy", "count": 3}
        )
        assert exhibit.status_code == 200
        assert len(exhibit.json()["objects"]) == 1

        deleted = client.delete(f"/api/objects/{object_id}")
        assert deleted.status_code == 204
