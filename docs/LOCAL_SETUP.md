# Run FleetOps locally on Windows

This guide is for running the four app services directly in PowerShell with SQLite, without Docker. To run the complete stack in containers with PostgreSQL, use [DOCKER_SETUP.md](DOCKER_SETUP.md).

## What you will run

| Service | Port / address | Purpose |
| --- | --- | --- |
| Django Web | <http://127.0.0.1:8000> | Browser dashboard |
| FastAPI API | <http://127.0.0.1:8001> | Vehicle and maintenance-job REST API |
| FastAPI BFF | <http://127.0.0.1:8002> | Web-facing API aggregation and forwarding |
| Python Worker | No HTTP port | Processes queued jobs in the background |

The local setup uses SQLite. All four processes must use the same `DATABASE_URL` and must be started from the project root so they share the same database file.

## 1. Open the project folder

Open the project folder in VS Code, then open a PowerShell terminal. Move to the project root (adjust this path if you put the folder somewhere else):

```powershell
Set-Location "C:\Users\Lenovo\OneDrive\Desktop\Ramesh Javali\CICD end to end"
```

You should see files such as `pyproject.toml`, `Plan.md`, and this `docs` folder:

```powershell
Get-ChildItem
```

## 2. Create and activate a Python environment

The project needs Python 3.12 or newer, but below 3.15. Check the Python version:

```powershell
python --version
```

Create a virtual environment once, then activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, you can avoid changing the execution policy and call the environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe --version
```

Install the app and its runtime dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

If you did not activate the environment, use `\.venv\Scripts\python.exe -m pip ...` instead of `python -m pip ...` in the commands below.

## 3. Create the local database schema

From the project root, set the database URL and Python import path, then apply the Alembic migration:

```powershell
$env:DATABASE_URL = "sqlite:///./fleetops.db"
$env:PYTHONPATH = "src"
python -m alembic upgrade head
```

This creates a `fleetops.db` file in the project root. The API and Worker also create missing tables on startup as a convenience, but running migrations first is the normal setup path.

## 4. Start the four services

Start **each service in its own VS Code PowerShell terminal**. Keep all four terminals open while using the app. In every terminal, first set the project root and the shared database settings.

### Terminal 1 — API

```powershell
Set-Location "C:\Users\Lenovo\OneDrive\Desktop\Ramesh Javali\CICD end to end"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
$env:DATABASE_URL = "sqlite:///./fleetops.db"
python -m uvicorn fleetops.services.api.main:app --host 127.0.0.1 --port 8001
```

The API's interactive docs are at <http://127.0.0.1:8001/docs>.

### Terminal 2 — BFF

```powershell
Set-Location "C:\Users\Lenovo\OneDrive\Desktop\Ramesh Javali\CICD end to end"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
$env:DATABASE_URL = "sqlite:///./fleetops.db"
$env:API_BASE_URL = "http://127.0.0.1:8001"
python -m uvicorn fleetops.services.bff.main:app --host 127.0.0.1 --port 8002
```

### Terminal 3 — Worker

```powershell
Set-Location "C:\Users\Lenovo\OneDrive\Desktop\Ramesh Javali\CICD end to end"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
$env:DATABASE_URL = "sqlite:///./fleetops.db"
python -m fleetops.services.worker.main
```

Leave this terminal running. It prints a message when it processes a job.

### Terminal 4 — Web

```powershell
Set-Location "C:\Users\Lenovo\OneDrive\Desktop\Ramesh Javali\CICD end to end"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
$env:DATABASE_URL = "sqlite:///./fleetops.db"
$env:BFF_BASE_URL = "http://127.0.0.1:8002"
python src/fleetops/services/web/manage.py runserver 127.0.0.1:8000 --noreload
```

Open the dashboard at <http://127.0.0.1:8000>.

## 5. Register a vehicle

Register a vehicle from the dashboard at <http://127.0.0.1:8000> using the **Register a vehicle** form. Or create one through the API in a fifth terminal, or any terminal that is not running a service:

```powershell
$vehicle = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8001/vehicles" `
  -ContentType "application/json" `
  -Body '{"registration":"DEMO-01","make":"Volvo","model":"FH","year":2023}'

$vehicle
```

A successful response contains the vehicle's numeric `id`. Registration values must be unique. If you repeat this step, choose a new registration such as `DEMO-02`.

## 6. Submit and observe a maintenance job

You can submit a job in either of these ways:

- On the dashboard, select the vehicle, choose a maintenance job (such as **Oil change**, **Brake inspection**, or **Tire rotation**), and click **Add to maintenance queue**. Choose **Other** to type a custom job.
- Or use the API directly (replace `1` with the `id` returned when you created the vehicle):

```powershell
$job = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8001/jobs" `
  -ContentType "application/json" `
  -Body '{"vehicle_id":1,"description":"Inspect brakes"}'

$job
```

The new job starts with status `queued`. The dashboard shows a color-coded guide to all four job statuses and refreshes Recent jobs automatically every two seconds. The Worker keeps the job in `processing` for two seconds by default so you can see that step before it becomes `completed`. To make the step last longer, set `$env:JOB_PROCESSING_SECONDS = "5"` in the Worker terminal before starting it; set it to `"0"` to turn off the demo delay.

The Worker should log that it processed the job. You can also query jobs and their current status with:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/jobs"
```

The BFF dashboard response is available at <http://127.0.0.1:8002/fleet>.

## 7. Check service health

Run these in a PowerShell terminal while the services are running:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/health/live"
Invoke-RestMethod -Uri "http://127.0.0.1:8001/health/ready"
Invoke-RestMethod -Uri "http://127.0.0.1:8002/health/live"
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/health/live"
```

The API readiness endpoint checks database connectivity. The other health endpoints confirm the corresponding HTTP service is responding.

## 8. Run automated checks

Stop or leave the services running; open a separate terminal at the project root and activate `.venv`. Then run:

```powershell
python -m pip install pytest pytest-cov pytest-django ruff mypy coverage
python -m pytest -q
python -m ruff check src tests migrations
python -m mypy src/fleetops
```

The tests use a separate SQLite test database file so they do not intentionally use the sample database.

## Stop the app and reset local data

To stop each service, focus its terminal and press **Ctrl+C**. Stop the API, BFF, Worker, and Web terminals.

To reset the local demo database after all services have stopped, remove the SQLite database file from the project root and reapply migrations:

```powershell
Remove-Item .\fleetops.db -ErrorAction SilentlyContinue
$env:DATABASE_URL = "sqlite:///./fleetops.db"
$env:PYTHONPATH = "src"
python -m alembic upgrade head
```

## Troubleshooting

### `No module named fleetops`

Make sure the terminal is at the project root, the virtual environment is active, and `$env:PYTHONPATH = "src"` has been set in that terminal. Alternatively, install the project with `python -m pip install -e .`.

### `Address already in use`

Another app process is already using that port. Stop the older service terminal with **Ctrl+C**, then start one instance of each service only. Web uses 8000, API 8001, and BFF 8002.

### Dashboard says fleet services are unavailable

Confirm API and BFF terminals are still running. In the Web terminal, check that `BFF_BASE_URL` is set to `http://127.0.0.1:8002`. In the BFF terminal, check that `API_BASE_URL` is set to `http://127.0.0.1:8001`.

### Vehicle/job is missing or the Worker does not see it

All service terminals must set the exact same `DATABASE_URL` and start from the repository root. For this setup, use `sqlite:///./fleetops.db` in every terminal. Check the Worker terminal for errors.

### Vehicle registration already exists

Registration is unique. Choose another value, for example `DEMO-02`.

## Other deployment options

This local setup does not require Docker or PostgreSQL. For Docker Compose, see [DOCKER_SETUP.md](DOCKER_SETUP.md). Helm, Kubernetes, GHCR, and GitHub Actions remain future project phases. See [ARCHITECTURE.md](ARCHITECTURE.md) for how the services fit together and [../Plan.md](../Plan.md) for the planned phases.
