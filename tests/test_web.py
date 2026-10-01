from unittest.mock import Mock, patch

from django.test import Client


def test_web_health_endpoint() -> None:
    response = Client().get("/health/live")
    assert response.status_code == 200
    assert response.content == b"alive"


@patch("fleetops.services.web.views.httpx.get")
def test_job_status_endpoint_returns_jobs(mock_get: Mock) -> None:
    upstream = Mock()
    upstream.json.return_value = [
        {"id": 7, "status": "processing", "description": "Inspect brakes"}
    ]
    mock_get.return_value = upstream

    response = Client().get("/jobs/status")

    assert response.status_code == 200
    assert response.json()["available"] is True
    assert response.json()["jobs"][0]["status"] == "processing"


@patch("fleetops.services.web.views.httpx.post")
def test_submit_job_forwards_selected_maintenance_type(mock_post: Mock) -> None:
    response_from_bff = Mock()
    mock_post.return_value = response_from_bff

    response = Client().post(
        "/jobs",
        {"vehicle_id": "1", "description": "Brake inspection"},
    )

    assert response.status_code == 302
    assert mock_post.call_args.kwargs["json"] == {
        "vehicle_id": "1",
        "description": "Brake inspection",
    }
