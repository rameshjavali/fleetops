import os

os.environ["DATABASE_URL"] = "sqlite:///./fleetops-tests.db"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fleetops.services.web.settings")

from fleetops.infrastructure.db import Base, engine  # noqa: E402,I001


# Keep each test run isolated from a developer's local application database.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
