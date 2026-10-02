# Automatically deploy to local Minikube

The GitHub Actions workflow can deploy FleetOps to Minikube on your Windows
computer using a **self-hosted runner**. The runner is a small program that
connects your computer to GitHub Actions and runs the deployment job locally.
Your PC must be on, connected to the internet, and running Minikube when the
job starts.

## One-time setup

1. Install and verify Docker Desktop and Minikube on the Windows computer
   where Minikube runs. Start Docker Desktop and Minikube:

   ```powershell
   minikube start
   minikube status
   ```

2. In the GitHub repository, open **Settings → Actions → Runners → New
   self-hosted runner**. Select **Windows** and the machine's architecture,
   then follow GitHub's current instructions to download and configure the
   runner. Add this custom runner label when prompted:

   ```text
   fleetops-minikube
   ```

   The standard `self-hosted` and `windows` labels are assigned automatically.
   Do not put the temporary registration token in the repository or share it.

3. Run the GitHub runner as the same Windows user that can access Docker
   Desktop and the Minikube profile. For the simplest local setup, start it
   from its extracted directory in a PowerShell window using the `run.cmd`
   command shown in GitHub's runner setup instructions. Keep that window open.
   Do not install it as a Windows service unless you have confirmed the service
   account can access Docker and Minikube.

4. In **Settings → Actions → Runners**, confirm the runner shows **Idle** and
   has the `fleetops-minikube` label.

## What happens after setup

On each push to `main`, GitHub Actions first runs tests, Ruff, mypy, and Helm
validation on a GitHub-hosted runner. If they pass, it builds and publishes
the image to GHCR. The self-hosted deployment job then:

1. Logs in to GHCR with the workflow's short-lived `GITHUB_TOKEN`.
2. Pulls the image tagged with the full commit SHA and loads it into Minikube.
3. Updates the existing `api`, `bff`, `web`, and `worker` Deployments to use
   the new image, without changing their Services or PostgreSQL storage.
4. Waits for the app Deployments to become ready and lists the pods and
   services.

Pull requests do not use the self-hosted runner. Do not add untrusted
pull-request jobs to a self-hosted runner: jobs on it can execute code on your
computer. Limit who can push to `main` and protect the branch, since changes
merged there can run on your computer.

## View the deployed app

After the deployment job succeeds, open the existing Web service:

```powershell
minikube service web -n fleetops
```

This job updates the existing Kubernetes deployments in place, so the service
name remains `web` and its URL is unchanged. The Helm chart can still be used
as a separate deployment option, but do not install it alongside this stack
unless you intend to run two copies of the app and database.

## If deployment does not start

- Check that the runner is online and idle in the repository's runner
  settings.
- Ensure Docker Desktop and the Minikube cluster are running under the same
  Windows user as the runner.
- Check the deployment job log in the GitHub Actions run.
- If GHCR denies access to a private package, open the package settings on
  GitHub and grant this repository access to the package.

To stop automatic deployment, stop the runner or remove it from the
repository's **Settings → Actions → Runners** page.
