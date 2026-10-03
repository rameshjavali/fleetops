# FleetOps

FleetOps is a small fleet-management demo and learning project. It lets you register vehicles, schedule maintenance, and watch a background worker process jobs. It demonstrates a multi-service Python application with both local development and Docker Compose setups.

> **Current stage:** Run locally with SQLite, Docker Compose and PostgreSQL, or deploy the demo to Minikube with the Helm chart. GitHub Actions runs checks and publishes the app image to GHCR; automatic Minikube deployment uses a self-hosted runner.

## What runs

| Service | What it does | Local address |
| --- | --- | --- |
| Web (Django) | Browser dashboard for vehicles and maintenance jobs | <http://127.0.0.1:8000> |
| API (FastAPI) | Stores vehicles and jobs; provides the REST API | <http://127.0.0.1:8001> |
| BFF (FastAPI) | UI-facing layer; gathers dashboard data and forwards job requests to the API | <http://127.0.0.1:8002> |
| Worker (Python) | Polls queued jobs and records completed or failed status | Background process; no browser port |

Local development uses a SQLite file. Docker Compose runs PostgreSQL and all four services. A job is stored with status `queued`; the Worker processes it and updates its status, which the dashboard refreshes automatically.

## Run with Docker

Follow [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md) for Docker Desktop setup, commands, app URLs, PostgreSQL/DBeaver connection details, and troubleshooting.

## Run with Minikube

Follow [docs/MINIKUBE_SETUP.md](docs/MINIKUBE_SETUP.md) for prerequisites and the one-command Windows PowerShell deployment.

## Run locally on Windows

Follow [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md) to run the services directly with Python and SQLite, without Docker.

## Project map

- `src/fleetops/domain/` — core FleetOps entities and statuses.
- `src/fleetops/application/` — validation and application rules.
- `src/fleetops/infrastructure/` — SQLAlchemy database models and data-access code.
- `src/fleetops/services/` — Django Web, FastAPI API, FastAPI BFF, and Worker entry points.
- `migrations/` — Alembic database migration history.
- `tests/` — automated tests for the rules, services, and worker flow.
- `docs/ARCHITECTURE.md` — beginner-friendly explanation of the request and job flow.
- `docs/DOCKER_SETUP.md` — Docker Compose startup, database connection, and troubleshooting.
- `docs/MINIKUBE_SETUP.md` — Minikube deployment instructions.
- `docs/HELM_CHART.md` — Helm chart resources, configuration, and commands.
- `docs/GITHUB_ACTIONS.md` — CI checks, GHCR image publishing, and automatic Minikube deployment.
- `docs/SONARQUBE_SETUP.md` — SonarQube and SonarCloud setup instructions for CI.
- `docs/SELF_HOSTED_RUNNER.md` — configure automatic GitHub Actions deployment to local Minikube.
- `docs/LOCAL_SETUP.md` — local installation and run instructions.
- `Plan.md` — phased project delivery plan.

## Run tests and quality checks

After installing the development tools, run these from the repository root:

```powershell
python -m pytest --cov=fleetops --cov-report=xml --cov-report=term-missing -q
python -m ruff check src tests migrations
python -m mypy src/fleetops
trivy fs --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1 .
```

For local development, install the runtime application first, then the test and quality tools:

```powershell
python -m pip install -e .
python -m pip install pytest pytest-cov pytest-django ruff mypy coverage
```

<!-- trigger workflow -->
<!-- sonar configuration updated -->

### SonarQube and Trivy in CI

The GitHub Actions workflow runs the repository checks and then scans the codebase and container image. To enable SonarQube analysis, add a `SONAR_TOKEN` secret and set the repository variables `SONAR_PROJECT_KEY` and `SONAR_HOST_URL` (for SonarCloud, `SONAR_HOST_URL` is usually `https://sonarcloud.io`). Trivy runs automatically on the filesystem and on the built image when the workflow publishes an image.

Follow [docs/SONARQUBE_SETUP.md](docs/SONARQUBE_SETUP.md) for step-by-step setup and troubleshooting.

## Current limitations

This is a learning/demo app, not a production fleet platform. It uses a simple database-polling worker. Authentication, authorization, production secrets, and cloud-specific infrastructure are not included. The self-hosted runner and local Minikube deployment are intended for development and learning, not production infrastructure.
