# FleetOps

FleetOps is a small fleet-management demo and learning project. It lets you view vehicles, choose a maintenance task (or enter a custom one), and watch a background worker process it. It is also being built to demonstrate a multi-service Python application and, in later phases, Docker, Kubernetes/Helm, and GitHub Actions CI/CD.

> **Current stage:** The four services run locally with SQLite. Docker/Compose, PostgreSQL, Helm, and GitHub Actions are planned phases and are not required to try the app today.

## What runs

| Service | What it does | Local address |
| --- | --- | --- |
| Web (Django) | Browser dashboard for vehicles and maintenance jobs | <http://127.0.0.1:8000> |
| API (FastAPI) | Stores vehicles and jobs; provides the REST API | <http://127.0.0.1:8001> |
| BFF (FastAPI) | UI-facing layer; gathers dashboard data and forwards job requests to the API | <http://127.0.0.1:8002> |
| Worker (Python) | Polls queued jobs and records completed or failed status | Background process; no browser port |

The app uses a local SQLite file by default. A job is stored in the database with status `queued`; the Worker polls for it, processes it, and changes its status. The Web dashboard reads the updated result through the BFF and API.

## Run it on Windows

Follow the full step-by-step guide in [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md). It covers Python setup, starting each service in its own VS Code terminal, creating sample data, checking that a job completes, and troubleshooting.

## Project map

- `src/fleetops/domain/` — core FleetOps entities and statuses.
- `src/fleetops/application/` — validation and application rules.
- `src/fleetops/infrastructure/` — SQLAlchemy database models and data-access code.
- `src/fleetops/services/` — Django Web, FastAPI API, FastAPI BFF, and Worker entry points.
- `migrations/` — Alembic database migration history.
- `tests/` — automated tests for the rules, services, and worker flow.
- `docs/ARCHITECTURE.md` — beginner-friendly explanation of the request and job flow.
- `docs/LOCAL_SETUP.md` — local installation and run instructions.
- `Plan.md` — phased project delivery plan.

## Run tests and quality checks

After installing the development tools, run these from the repository root:

```powershell
python -m pytest -q
python -m ruff check src tests migrations
python -m mypy src/fleetops
```

For local development, install the runtime application first, then the test and quality tools:

```powershell
python -m pip install -e .
python -m pip install pytest pytest-cov pytest-django ruff mypy coverage
```

## Current limitations

This is a learning/demo app, not a production fleet platform. The current local run uses SQLite and a simple database-polling worker. Authentication, authorization, production secrets, and cloud-specific infrastructure are not included. PostgreSQL, containerized local development, Helm deployments, and CI/CD are future plan phases.
