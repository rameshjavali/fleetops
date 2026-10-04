import httpx
from fastapi.testclient import TestClient

from fleetops.services.bff import main as bff


def test_bff_composes_dashboard(monkeypatch) -> None:
    def fake_call_api(
        method: str,
        path: str,
        *,
        json_body: dict[str, int | str] | None = None,
    ) -> httpx.Response:
        del method, json_body
        payload = [{"id": 1, "registration": "TEST-01"}] if path == "/vehicles" else []
        return httpx.Response(200, json=payload, request=httpx.Request("GET", f"http://api{path}"))

    monkeypatch.setattr(bff, "call_api", fake_call_api)
    with TestClient(bff.app) as client:
        response = client.get("/fleet")
    assert response.status_code == 200
    assert response.json() == {"vehicles": [{"id": 1, "registration": "TEST-01"}], "jobs": []}


def test_bff_creates_vehicle(monkeypatch) -> None:
    def fake_call_api(
        method: str,
        path: str,
        *,
        json_body: dict[str, int | str] | None = None,
    ) -> httpx.Response:
        assert method == "POST"
        assert path == "/vehicles"
        assert json_body is not None
        return httpx.Response(
            201,
            json={"id": 1, **json_body},
            request=httpx.Request(method, f"http://api{path}"),
        )

    monkeypatch.setattr(bff, "call_api", fake_call_api)
    with TestClient(bff.app) as client:
        response = client.post(
            "/vehicles",
            json={"registration": "TEST-02", "make": "Volvo", "model": "FH", "year": 2023},
        )

    assert response.status_code == 201
    assert response.json()["registration"] == "TEST-02"


def test_bff_lists_jobs(monkeypatch) -> None:
    def fake_call_api(
        method: str,
        path: str,
        *,
        json_body: dict[str, int | str] | None = None,
    ) -> httpx.Response:
        del json_body
        assert method == "GET"
        assert path == "/jobs"
        return httpx.Response(
            200,
            json=[{"id": 1, "status": "queued"}],
            request=httpx.Request(method, f"http://api{path}"),
        )

    monkeypatch.setattr(bff, "call_api", fake_call_api)
    with TestClient(bff.app) as client:
        response = client.get("/jobs")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "status": "queued"}]


def test_bff_submits_job(monkeypatch) -> None:
    def fake_call_api(
        method: str,
        path: str,
        *,
        json_body: dict[str, int | str] | None = None,
    ) -> httpx.Response:
        assert method == "POST"
        assert path == "/jobs"
        assert json_body == {"vehicle_id": 1, "description": "Inspect brakes"}
        return httpx.Response(
            202,
            json={"id": 7, "status": "queued"},
            request=httpx.Request(method, f"http://api{path}"),
        )

    monkeypatch.setattr(bff, "call_api", fake_call_api)
    with TestClient(bff.app) as client:
        response = client.post(
            "/jobs",
            json={"vehicle_id": 1, "description": "Inspect brakes"},
        )

    assert response.status_code == 202
    assert response.json() == {"id": 7, "status": "queued"}
