from django.urls import path

from fleetops.services.web.views import home, job_status, live, register_vehicle, submit_job

urlpatterns = [
    path("", home, name="home"),
    path("vehicles", register_vehicle, name="register_vehicle"),
    path("jobs", submit_job, name="submit_job"),
    path("jobs/status", job_status, name="job_status"),
    path("health/live", live, name="live"),
]
