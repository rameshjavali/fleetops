from sqlalchemy import select
from sqlalchemy.orm import Session

from fleetops.infrastructure.db import JobRecord, VehicleRecord


class FleetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_vehicles(self) -> list[VehicleRecord]:
        return list(self.session.scalars(select(VehicleRecord).order_by(VehicleRecord.id)))

    def get_vehicle(self, vehicle_id: int) -> VehicleRecord | None:
        return self.session.get(VehicleRecord, vehicle_id)

    def add_vehicle(self, *, registration: str, make: str, model: str, year: int) -> VehicleRecord:
        vehicle = VehicleRecord(registration=registration, make=make, model=model, year=year)
        self.session.add(vehicle)
        self.session.flush()
        return vehicle

    def list_jobs(self) -> list[JobRecord]:
        return list(self.session.scalars(select(JobRecord).order_by(JobRecord.id.desc())))

    def add_job(self, *, vehicle_id: int, description: str) -> JobRecord:
        job = JobRecord(vehicle_id=vehicle_id, description=description)
        self.session.add(job)
        self.session.flush()
        return job
