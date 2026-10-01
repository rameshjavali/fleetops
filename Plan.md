# FleetOps Python CI/CD Project Plan

## Goal

Build a runnable fleet-management sample that mirrors the supplied .NET project prompt, using Python in place of .NET while retaining its four deployable components, layered architecture, Docker, Kubernetes/Helm, GitHub Actions, scans, and documentation.

## Technology choices

- **Python:** 3.12, managed with `uv` and a committed lockfile.
- **Web:** Django templates for a server-rendered MVC-style UI.
- **REST API and BFF:** Separate FastAPI services.
- **Background processing:** Python worker with a durable PostgreSQL-backed job queue, keeping Postgres as the only local infrastructure dependency.
- **Shared layers:** Domain, Application, Infrastructure, and DAL; SQLAlchemy and Alembic provide persistence and migrations.
- **Tests and quality:** pytest, coverage, Ruff, and type checking.
- **Delivery:** Docker Compose locally; Helm and GitHub Actions for Kubernetes CI/CD.

## Phase 1 — Python solution foundation and working services

**Purpose:** Create the repository structure and a minimal end-to-end FleetOps workflow before adding infrastructure automation.

1. Establish a Python monorepo with `uv`, Python 3.12, a lockfile, shared tool configuration, and separate packages for the services and shared layers.
2. Create four runnable applications:
   - `web`: Django UI for viewing vehicles and submitting or viewing a maintenance/delivery job.
   - `api`: FastAPI system-of-record endpoints for vehicles and jobs, with OpenAPI and health endpoints.
   - `bff`: FastAPI UI-facing endpoints that call the API and handle downstream timeouts/errors.
   - `worker`: Python process that takes queued jobs and records completion/failure.
3. Create shared Domain, Application, Infrastructure, and DAL packages. Keep domain rules independent from Django/FastAPI and database frameworks.
4. Add SQLAlchemy models/repositories and Alembic migrations for vehicles and jobs. Use Postgres for application data and a durable job queue; the worker claims pending rows with database locking.
5. Implement the complete basic flow: Web → BFF → API → Postgres; enqueue a job; worker processes it; job status is visible through the API/UI.
6. Add pytest tests for domain/application rules, persistence, API and BFF contracts, Django views, and worker job lifecycle. Include liveness/readiness endpoints and test them.

**Phase 1 acceptance checks**

- All four services start independently and expose their expected entry points.
- Migrations create the schema; vehicle/job data persists.
- A user can view fleet data and submit a job; the worker can process it and the resulting status can be read.
- Unit and service tests pass; no service is only a stub.

## Phase 2 — Dockerfiles and local Compose

**Purpose:** Make the application easy to run locally and establish the same container build path used by CI.

1. Add one multi-stage Dockerfile per deployable component: Web, API, BFF, and Worker. Use dependency install/build/runtime stages appropriate to Python; run as non-root where practical.
2. Add a Compose manifest for all four services and Postgres, with a persistent database volume, internal networking, environment-based configuration, health checks, and dependency/startup ordering.
3. Run migrations through a clearly documented one-shot step or service; avoid race-prone implicit schema creation on every app startup.
4. Add a smoke-check path for service health, the Web/BFF/API request flow, and worker completion.

**Phase 2 acceptance checks**

- Compose configuration validates and all containers build.
- A clean local startup and migration work from the README instructions.
- The end-to-end fleet/job workflow works through Compose.
- No credentials are committed; local sample configuration is clearly marked for development.

## Phase 3 — Helm chart and environment overlays

**Purpose:** Deploy the four app services consistently to local or remote Kubernetes clusters.

1. Create one Helm chart with `values-dev.yaml`, `values-qa.yaml`, and `values-prod.yaml` overlays.
2. Add Deployment and Service templates for Web, API, BFF, and Worker. Route external Web traffic through Ingress; keep API/BFF/worker and database paths internal as appropriate.
3. Add HPA templates (autoscaling/v2) for scalable services, resource requests/limits, startup/readiness/liveness probes, replica settings, and rolling-update configuration.
4. Add NetworkPolicy templates with least-privilege service ingress/egress rules. Document that enforcement requires a supporting CNI; HPA requires a metrics provider.
5. Add ConfigMaps for non-secret environment configuration. Reference pre-created, environment-specific Kubernetes Secrets for credentials; never store production secrets in Helm values or source control.
6. Use externally provisioned Postgres for qa/prod. Document a suitable local Postgres setup for kind/k3d/Rancher Desktop without coupling production app releases to a bundled database.

**Phase 3 acceptance checks**

- `helm lint` succeeds and templates render for dev, qa, and prod.
- Rendered manifests include the four workloads, Services, Ingress, HPA, NetworkPolicies, and ConfigMap/Secret references.
- Environment overlays differ only in intended settings and contain no live secrets.

## Phase 4 — GitHub Actions CI/CD, analysis, and security scans

**Purpose:** Validate changes, publish immutable images, and deploy through controlled environments.

1. Trigger workflows for pull requests and pushes to `main`; use locked dependencies and least-privilege GitHub token permissions.
2. On pull requests, run dependency installation, linting, type checks, pytest with coverage, SonarCloud analysis, Trivy filesystem scanning, Docker build validation without publishing, and Helm lint/template validation for all overlays.
3. On `main`, after validation succeeds, build and push all four service images to GHCR tagged with the full Git commit SHA. Run Trivy image scans against the built images.
4. Deploy the exact SHA-tagged images to dev using `helm upgrade --install` after required checks pass.
5. Configure GitHub Actions secrets for SonarCloud and cluster credentials; use GitHub's supported GHCR permissions/authentication. Never expose deployment secrets to pull-request code, especially forked PRs.
6. Protect qa/prod with GitHub Environments and required manual approval. Promote the already-built SHA-tagged artifact instead of rebuilding it.

**Phase 4 acceptance checks**

- PR workflows validate but never push images or deploy.
- Main workflow publishes SHA-tagged images, scans them, then deploys dev.
- qa/prod promotion is gated; credentials are environment-scoped and not checked into the repository.
- SonarCloud and Trivy results are visible in workflow output; coverage is uploaded to analysis.

## Phase 5 — Documentation and local Kubernetes walkthrough

**Purpose:** Make the sample understandable and reproducible for a new developer or reviewer.

1. Write the root README with architecture, prerequisites, local Compose startup, migrations, tests, service URLs, configuration, and troubleshooting.
2. Write a Kubernetes guide for installing/starting kind, k3d, or Rancher Desktop; setting up ingress, metrics, NetworkPolicy-capable networking, and Postgres; creating secrets; deploying/upgrading Helm; and promoting environments.
3. Explain which requirements depend on cluster add-ons or external credentials and provide safe example values without secrets.

**Phase 5 acceptance checks**

- A reader can run the application locally from a clean checkout using documented instructions.
- A reader can deploy the chart to a supported local cluster and verify service health.
- The deployment and secret-promotion model is clear and contains no real credentials.

## Phase 6 — End-to-end verification and polish

1. Run `uv sync`, Ruff, type checking, pytest, and coverage; fix regressions before proceeding.
2. Validate Compose and build all four service images; run local smoke tests for UI, API/BFF, database persistence, and worker jobs.
3. Run Trivy filesystem/image scans and validate SonarCloud coverage integration when credentials are available.
4. Run Helm lint and render all environment overlays; inspect probes, resources, image tags, ConfigMaps, Secret references, Ingress, HPA, and NetworkPolicies.
5. Deploy to kind/k3d/Rancher Desktop when the necessary local tools are installed; smoke-test ingress, health endpoints, and worker processing.
6. Review workflow permissions and gates: PR validation only, main-to-dev, protected qa/prod promotion.

## Overall completion criteria

- Four independently deployable, minimally functional Python services plus shared layers and tests.
- Per-service multi-stage Dockerfiles and working local Compose with Postgres.
- Helm templates and dev/qa/prod overlays covering Deployment, Service, Ingress, HPA, NetworkPolicy, ConfigMap, and Secret handling.
- GitHub Actions for PR/main checks, GHCR SHA-tagged builds, SonarCloud, Trivy filesystem/image scans, dev deployment, and gated promotion.
- Root README and local Kubernetes deployment guide.
- Automated checks pass; any verification that requires external credentials or unavailable cluster tooling is clearly identified rather than claimed as completed.

## Delivery sequence

Implement and verify one phase at a time. Do not start the next phase until the current phase's acceptance checks pass, except for documentation that is needed to run that phase.
