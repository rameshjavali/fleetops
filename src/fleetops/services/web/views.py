import logging

import httpx
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


def live(_: HttpRequest) -> HttpResponse:
    return HttpResponse("alive", content_type="text/plain")


def home(request: HttpRequest) -> HttpResponse:
    try:
        response = httpx.get(
            f"{settings.BFF_BASE_URL}/fleet",
            timeout=8.0,
            trust_env=False,
        )
        response.raise_for_status()
        data = response.json()
        context = {
            "vehicles": data.get("vehicles", []),
            "jobs": data.get("jobs", []),
            "api_available": True,
        }
    except httpx.HTTPError:
        logger.exception("BFF request failed")
        context = {"vehicles": [], "jobs": [], "api_available": False}
    return render(request, "fleetops/home.html", context)


def job_status(request: HttpRequest) -> JsonResponse:
    try:
        response = httpx.get(
            f"{settings.BFF_BASE_URL}/jobs",
            timeout=8.0,
            trust_env=False,
        )
        response.raise_for_status()
        return JsonResponse({"jobs": response.json(), "available": True})
    except httpx.HTTPError:
        logger.exception("Could not refresh job statuses")
        return JsonResponse(
            {"jobs": [], "available": False},
            status=503,
        )


@require_POST  # type: ignore[untyped-decorator]
def register_vehicle(request: HttpRequest) -> HttpResponse:
    payload = {
        "registration": request.POST.get("registration", "").strip(),
        "make": request.POST.get("make", "").strip(),
        "model": request.POST.get("model", "").strip(),
        "year": request.POST.get("year", ""),
    }
    try:
        response = httpx.post(
            f"{settings.BFF_BASE_URL}/vehicles",
            json=payload,
            timeout=8.0,
            trust_env=False,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        logger.exception("Vehicle registration failed")
        return HttpResponse(
            "Could not register vehicle; check the details and try again.",
            status=502,
        )
    return redirect("home")


@require_POST  # type: ignore[untyped-decorator]
def submit_job(request: HttpRequest) -> HttpResponse:
    payload = {
        "vehicle_id": request.POST.get("vehicle_id"),
        "description": request.POST.get("description", ""),
    }
    try:
        response = httpx.post(
            f"{settings.BFF_BASE_URL}/jobs",
            json=payload,
            timeout=8.0,
            trust_env=False,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        logger.exception("Job submission failed")
        return HttpResponse("Could not submit job; please try again.", status=502)
    return redirect("home")
