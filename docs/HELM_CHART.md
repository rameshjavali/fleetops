# Helm, explained simply

Helm is a tool for installing and managing applications on Kubernetes. A
Kubernetes app usually needs several YAML files: for example, Deployments to
run containers, Services so containers can reach each other, and storage for
the database. Helm groups those files into a **chart** and installs or updates
them together.

A simple way to think about it:

- Kubernetes runs the containers and other resources.
- A Helm **chart** is the reusable package of instructions and templates for
  those resources.
- A Helm **release** is one installed copy of a chart in a cluster. We named
  our release `fleetops`.
- The chart's `values.yaml` contains settings, such as image name, replica
  counts, database storage, and local demo credentials.

Instead of manually applying each Kubernetes YAML file, we ask Helm to install
the FleetOps chart. Helm creates the Kubernetes resources and remembers the
release, so we can update or remove the app as one unit.

## How we set up this chart

Before Helm, the Kubernetes configuration was in separate files under
[`k8s/`](../k8s/). Those files described the namespace, database and storage,
and the API, BFF, Web, and Worker.

We packaged the same app setup into
[`helm/fleetops/`](../helm/fleetops/):

- `Chart.yaml` identifies the chart and its version.
- `values.yaml` holds settings that can be changed without editing the
  templates.
- `templates/` contains the Kubernetes resource definitions. Helm fills in
  names, image settings, replica counts, and other values when it installs the
  chart.

The chart includes PostgreSQL, its persistent volume claim and credentials
Secret, and the API, BFF, Web, and Worker workloads. All four app workloads use
the same `fleetops-api:local` image, as in the existing Minikube setup. Web is
exposed through a NodePort; the API, BFF, and database remain internal
ClusterIP services.

## What the current setup runs

- One replica each for API, BFF, Web, Worker, and PostgreSQL.
- PostgreSQL 16 Alpine with a 2 GiB persistent volume.
- The API listens on port 8001, the BFF on 8002, and Web on 8000.
- Web calls the BFF, which calls the API. The app services and Worker use
  PostgreSQL.
- Local-demo credentials and Django secret key are in
  [`values.yaml`](../helm/fleetops/values.yaml). They are not suitable for
  production.

## Use it on Minikube

You need Docker Desktop, Minikube, and Helm installed. Run these commands from
the repository root in PowerShell.

### 1. Build and load the app image

The chart points to a local image. Build it, then load it into Minikube so the
cluster can use it:

```powershell
docker build -t fleetops-api:local -f Dockerfile.api .
minikube image load fleetops-api:local
```

### 2. Install the chart

```powershell
helm upgrade --install fleetops .\helm\fleetops --namespace fleetops --create-namespace --wait
```

In this command, `fleetops` is the release name and `.\helm\fleetops` is the
chart directory. `--namespace fleetops` selects the Kubernetes namespace,
`--create-namespace` creates it if it does not exist, and `--wait` makes Helm
wait for the resources to become ready.

`upgrade --install` is convenient because the same command works both ways:
the first time, Helm installs the release; if the release already exists, Helm
applies changes to update it.

### 3. Open the app

```powershell
minikube service fleetops-web -n fleetops
```

Minikube prints or opens the local address for the dashboard. Keep the command
running if it starts a local tunnel.

## Change settings

Edit the appropriate setting in
[`values.yaml`](../helm/fleetops/values.yaml), or create a separate file and
pass it with `--values`. For example, to use different local-demo credentials
without editing the chart's defaults, make `my-values.yaml`:

```yaml
database:
  password: replace-this-for-local-use

django:
  secretKey: replace-this-for-local-use
```

Then install or update with that file:

```powershell
helm upgrade --install fleetops .\helm\fleetops --namespace fleetops --create-namespace --wait --values .\my-values.yaml
```

Do not commit real passwords or secret keys in a values file. For a shared or
production environment, use Kubernetes Secret management appropriate to that
environment rather than the chart's demo defaults.

## Check, update, or remove the release

List the Helm releases in the namespace:

```powershell
helm list -n fleetops
```

Check Kubernetes resources and view the API logs:

```powershell
minikube kubectl -- get pods,services,pvc -n fleetops
minikube kubectl -- logs deployment/fleetops-api -n fleetops
```

To apply later chart or values changes, rerun the `helm upgrade --install`
command. To remove the app resources:

```powershell
helm uninstall fleetops -n fleetops
```

The chart keeps the PostgreSQL claim when the release is removed, so the
database data is not automatically deleted. If you are sure you no longer need
that data, delete the claim explicitly:

```powershell
minikube kubectl -- delete pvc fleetops-postgres-data -n fleetops
```

The original Kubernetes YAML files in `k8s/` remain available. The automated
GitHub Actions deployment currently updates those existing app Deployments in
place to preserve the running service names and database storage. Installing
the Helm chart creates a separate set of resources; avoid installing both
setups in the same namespace unless you intentionally want two app/database
stacks.
