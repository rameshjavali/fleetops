from django.urls import path

from fleetops.services.web.views import home, job_status, live, submit_job

urlpatterns = [
    path("", home, name="home"),
    path("jobs", submit_job, name="submit_job"),
    path("jobs/status", job_status, name="job_status"),
    path("health/live", live, name="live"),
]
