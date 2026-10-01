import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "local-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,web").split(",")
ROOT_URLCONF = "fleetops.services.web.urls"
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.staticfiles"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(__file__).parent / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    }
]
ASGI_APPLICATION = "fleetops.services.web.asgi.application"
WSGI_APPLICATION = "fleetops.services.web.wsgi.application"
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
BFF_BASE_URL = os.getenv("BFF_BASE_URL", "http://localhost:8002").rstrip("/")
