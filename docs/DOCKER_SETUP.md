# Run FleetOps with Docker Compose

This guide runs the Web, API, BFF, Worker, and PostgreSQL services in Docker. The local Python/SQLite setup is documented in [LOCAL_SETUP.md](LOCAL_SETUP.md).

## Prerequisites

- Docker Desktop installed and running
- On Windows, Docker Desktop configured to use the Linux container engine
- PowerShell opened in the repository root (the folder containing `docker-compose.yml`)

Check Docker is available:

```powershell
docker --version
docker compose version
```

## Start the application

Build the images and start all services:

```powershell
docker compose up --build -d
```

Check that the services are running:

```powershell
docker compose ps
```

Open these addresses in your browser:

| Service | URL |
| --- | --- |
| FleetOps dashboard | <http://localhost:8000> |
| API interactive docs | <http://localhost:8001/docs> |
| BFF fleet data | <http://localhost:8002/fleet> |

The dashboard starts with an empty database. Use its **Register a vehicle** form to add a vehicle. Then schedule a maintenance job from the dashboard; the Worker updates its status.

## PostgreSQL and DBeaver

Compose publishes PostgreSQL on host port `5432`. To connect with DBeaver, create or edit a PostgreSQL connection with:

| Setting | Value |
| --- | --- |
| Host | `localhost` |
| Port | `5432` |
| Database | `fleetops` |
| Username | `fleetops` |
| Password | `secret` |

After connecting, expand **fleetops → Schemas → public → Tables**. The application tables are `vehicles` and `maintenance_jobs`. If the database or tables are not shown, refresh the connection and its database tree.

Containers connect to PostgreSQL using the Compose service hostname `db` and internal port `5432`; use `localhost` only from Windows applications such as DBeaver.

## Useful commands

View service status:

```powershell
docker compose ps
```

Follow logs for all services, or one service:

```powershell
docker compose logs -f
docker compose logs -f api
```

Stop the services while keeping database data:

```powershell
docker compose down
```

Start them again later with `docker compose up -d`. Database data is stored in the named `postgres_data` volume and is preserved by `docker compose down`.

**Warning:** This removes the database volume and all saved vehicles/jobs:

```powershell
docker compose down -v
```

## Troubleshooting

### Port 5432 is already in use

Another PostgreSQL server or container is listening on that host port. Stop the other server, or change the `db` service port mapping in `docker-compose.yml` from `5432:5432` to `5433:5432`. Recreate the stack with `docker compose up -d`. If using the alternate mapping, connect DBeaver to port `5433`; other containers still use `db:5432`.

### Dashboard says services are unavailable

Check that all services are up with `docker compose ps`, then inspect logs with `docker compose logs -f`. The Web service connects to the BFF, which connects to the API; the API and Worker both use the Compose PostgreSQL database.

### Docker images do not appear in WSL

On Windows, Docker Desktop is the engine used by this setup. Enable Docker Desktop's WSL integration for your Linux distribution if you want to run Docker commands from WSL. You can also run the commands from PowerShell.
