import os
from typing import cast

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001").rstrip("/")
app = FastAPI(title="FleetOps BFF", version="0.1.0")


class JobCreate(BaseModel):
    vehicle_id: int = Field(gt=0)
    description: str = Field(min_length=1, max_length=500)


def call_api(
    method: str,
    path: str,
    *,
    json_body: dict[str, int | str] | None = None,
) -> httpx.Response:
    try:
        with httpx.Client(base_url=API_BASE_URL, timeout=10.0, trust_env=False) as client:
            response = client.request(method, path, json=json_body)
            response.raise_for_status()
            return response
    except (httpx.HTTPError, httpx.TimeoutException) as exc:
        raise HTTPException(status_code=503, detail="Fleet API is unavailable") from exc


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/fleet")
def fleet_dashboard() -> dict[str, object]:
    vehicles = call_api("GET", "/vehicles")
    jobs = call_api("GET", "/jobs")
    return {"vehicles": vehicles.json(), "jobs": jobs.json()}


@app.get("/jobs")
def list_jobs() -> list[dict[str, object]]:
    response = call_api("GET", "/jobs")
    return cast(list[dict[str, object]], response.json())


@app.post("/jobs", status_code=202)
def submit_job(payload: JobCreate) -> dict[str, object]:
    response = call_api(
        "POST",
        "/jobs",
        json_body={"vehicle_id": payload.vehicle_id, "description": payload.description},
    )
    return cast(dict[str, object], response.json())
