# GitHub Actions CI and image publishing

The workflow at
[`main.yml`](../.github/workflows/main.yml) automates project checks, publishes
the application Docker image to GitHub Container Registry (GHCR), and can
deploy to local Minikube through a self-hosted Windows runner. Follow
[`SELF_HOSTED_RUNNER.md`](SELF_HOSTED_RUNNER.md) for the one-time runner setup.
Without that runner online, the deployment job waits for a matching runner.

## What runs automatically

For every push and pull request, GitHub Actions:

1. Installs the project and its test/quality tools using Python 3.12.
2. Runs the tests, Ruff, and mypy.
3. Lints and renders the Helm chart.

If those checks pass for a push to `main` or a version tag beginning with `v`
(for example, `v1.0.0`), a second job builds the image from `Dockerfile.api`
and pushes it to GHCR. A push to `main` then triggers deployment to Minikube
through the self-hosted runner. Version tags publish an image but do not
deploy it. The workflow uses GitHub's `GITHUB_TOKEN`; no registry password
needs to be added as a repository secret.

The automatic deployment updates the existing Kubernetes Deployments named
`api`, `bff`, `web`, and `worker` in the `fleetops` namespace. It does not
install the Helm chart or replace the database, Services, or persistent data.

Images are tagged with the full commit SHA, for example
`ghcr.io/rameshjavali/fleetops:sha-<full-commit-sha>`. A push to `main` also updates
the `main` and `latest` tags. A version tag such as `v1.0.0` publishes an
image tagged `v1.0.0`.

## Manually deploy a published image to Minikube

This is an alternative to automatic deployment. After the image-publishing
job succeeds:

1. Open the successful workflow run in GitHub Actions and copy the commit SHA.
2. From PowerShell, pull the image and load it into your local Minikube:

   ```powershell
   $CommitSha = "paste-full-commit-sha-here"
   docker pull "ghcr.io/rameshjavali/fleetops:sha-$CommitSha"
   minikube image load "ghcr.io/rameshjavali/fleetops:sha-$CommitSha"
   ```

   Replace the sample value with the full SHA from the run.

3. Update the existing app Deployments to use that image:

   ```powershell
   $Image = "ghcr.io/rameshjavali/fleetops:sha-$CommitSha"
   $Deployments = @("api", "bff", "web", "worker")
   foreach ($Deployment in $Deployments) {
     minikube kubectl -- set image "deployment/$Deployment" "$Deployment=$Image" -n fleetops
     if ($LASTEXITCODE -ne 0) { throw "Failed to update deployment/$Deployment" }
   }
   foreach ($Deployment in $Deployments) {
     minikube kubectl -- rollout status "deployment/$Deployment" -n fleetops --timeout=180s
     if ($LASTEXITCODE -ne 0) { throw "deployment/$Deployment did not become ready" }
   }
   ```

   This updates the current workloads in place and leaves the `web` service
   name and database storage unchanged.

4. Open the app:

   ```powershell
   minikube service web -n fleetops
   ```

If GHCR asks for authentication when pulling the image, sign in to `ghcr.io`
using your GitHub username and a personal access token with `read:packages`
permission:

```powershell
docker login ghcr.io -u rameshjavali
```

Do not put the token in this repository, a command recorded in shared logs, or
a committed values file. If the package is private, you must authenticate
before pulling. A package owner can adjust the package visibility in its
GitHub package settings.

## Important distinction

The automated workflow updates the original deployments from `k8s/` in place,
so the Web service remains `web` and existing database storage is preserved.
The Helm chart is validated by CI and remains available as a separate
deployment option; installing it creates a separate set of resources and is
not part of this automated deployment.
