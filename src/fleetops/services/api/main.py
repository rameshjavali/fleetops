from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fleetops.application.fleet import FleetValidationError, validate_job, validate_vehicle
from fleetops.infrastructure.dal import FleetRepository
from fleetops.infrastructure.db import SessionLocal, initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(title="FleetOps API", version="0.1.0", lifespan=lifespan)


class VehicleCreate(BaseModel):
    registration: str = Field(min_length=1, max_length=32)
    make: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    year: int


class VehicleRead(VehicleCreate):
    id: int


class JobCreate(BaseModel):
    vehicle_id: int = Field(gt=0)
    description: str = Field(min_length=1, max_length=500)


class JobRead(JobCreate):
    id: int
    status: str
    result: str | None = None


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def readiness(session: Session = Depends(get_session)) -> dict[str, str]:
    try:
        session.connection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    return {"status": "ready"}


@app.get("/vehicles", response_model=list[VehicleRead])
def list_vehicles(session: Session = Depends(get_session)) -> list[VehicleRead]:
    return [
        VehicleRead.model_validate(row, from_attributes=True)
        for row in FleetRepository(session).list_vehicles()
    ]


@app.post("/vehicles", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, session: Session = Depends(get_session)) -> VehicleRead:
    try:
        validate_vehicle(payload.registration, payload.make, payload.model, payload.year)
        row = FleetRepository(session).add_vehicle(**payload.model_dump())
        session.flush()
    except FleetValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Registration already exists") from exc
    return VehicleRead.model_validate(row, from_attributes=True)


@app.get("/jobs", response_model=list[JobRead])
def list_jobs(session: Session = Depends(get_session)) -> list[JobRead]:
    return [
        JobRead.model_validate(row, from_attributes=True)
        for row in FleetRepository(session).list_jobs()
    ]


@app.post("/jobs", response_model=JobRead, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: JobCreate, session: Session = Depends(get_session)) -> JobRead:
    try:
        validate_job(payload.vehicle_id, payload.description)
    except FleetValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if FleetRepository(session).get_vehicle(payload.vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    row = FleetRepository(session).add_job(**payload.model_dump())
    session.flush()
    return JobRead.model_validate(row, from_attributes=True)
