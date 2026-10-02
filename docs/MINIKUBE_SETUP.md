# Run FleetOps with Minikube

This guide deploys the Web, API, BFF, Worker, and PostgreSQL services to a local Minikube cluster on Windows.

## Prerequisites

- Docker Desktop installed and running with the Linux container engine
- Minikube installed
- PowerShell opened in the repository root, or invoke the script by its full path

Check that Docker and Minikube are available:

```powershell
docker info
minikube version
```

## Build and deploy

From the repository root, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\deploy-minikube.ps1
```

The script starts Minikube with Docker (2 CPUs, 3 GiB memory, Kubernetes 1.35.1), builds and loads one shared FleetOps image (to reduce disk use), installs or upgrades the Helm chart in `helm/fleetops/`, and waits for the workloads to become ready. Helm must be installed and available on `PATH`.
The execution-policy bypass applies only to this PowerShell process; it does not change the machine's policy.

If Minikube is already running and you do not want the script to start it again:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\deploy-minikube.ps1 -SkipMinikubeStart
```

## Run it again after stopping Minikube

If you stopped Minikube but did not delete the cluster, start the existing cluster:

```powershell
minikube start -p minikube
```

Wait for all FleetOps pods to be ready:

```powershell
minikube kubectl -- get pods -n fleetops
```

When the pods show `1/1` under `READY`, start the dashboard tunnel again:

```powershell
minikube service fleetops-web -n fleetops --url
```

Open the URL printed by Minikube and keep that PowerShell terminal open while using the app. You do not need to rebuild the images or redeploy unless you changed the code or deleted the cluster.

To open the dashboard:

```powershell
minikube service fleetops-web -n fleetops
```

Keep that command's terminal open while using the app; it may run a local tunnel. The API and BFF are internal cluster services. To access the API docs from Windows, use a separate terminal:

```powershell
minikube kubectl -- port-forward service/fleetops-api 8001:8001 -n fleetops
```

Then visit <http://localhost:8001/docs>.

## Check status and logs

```powershell
minikube kubectl -- get pods -n fleetops
minikube kubectl -- get services -n fleetops
minikube kubectl -- logs deployment/fleetops-api -n fleetops
```

The PostgreSQL data is stored in the `fleetops-postgres-data` persistent volume claim. Remove the Helm release while preserving that data with:

```powershell
helm uninstall fleetops -n fleetops
```

To also delete the database data, delete the PVC explicitly:

```powershell
minikube kubectl -- delete pvc fleetops-postgres-data -n fleetops
```

## Notes

The chart includes demo-only credentials and a Django secret key for a local learning cluster. Override them for any shared environment, and use production-grade secret management for production deployments. See [HELM_CHART.md](HELM_CHART.md) for chart details and values.
