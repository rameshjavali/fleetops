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
