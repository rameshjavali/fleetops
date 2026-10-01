from fastapi.testclient import TestClient

from fleetops.services.api.main import app
from fleetops.services.worker.main import process_one


def test_api_creates_fleet_and_worker_completes_job() -> None:
    with TestClient(app) as client:
        vehicle_response = client.post(
            "/vehicles",
            json={"registration": "TEST-01", "make": "Volvo", "model": "FH", "year": 2023},
        )
        assert vehicle_response.status_code == 201
        vehicle_id = vehicle_response.json()["id"]

        job_response = client.post(
            "/jobs", json={"vehicle_id": vehicle_id, "description": "Inspect brakes"}
        )
        assert job_response.status_code == 202
        job_id = job_response.json()["id"]
        assert job_response.json()["status"] == "queued"

        assert process_one(processing_delay=0) == job_id
        completed = client.get("/jobs").json()[0]
        assert completed["id"] == job_id
        assert completed["status"] == "completed"
        assert completed["result"] == "Completed: Inspect brakes"


def test_api_rejects_job_for_unknown_vehicle() -> None:
    with TestClient(app) as client:
        response = client.post("/jobs", json={"vehicle_id": 99999, "description": "Inspect"})
    assert response.status_code == 404


def test_worker_returns_none_when_queue_is_empty() -> None:
    with TestClient(app):
        assert process_one(processing_delay=0) is None
