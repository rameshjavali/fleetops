from dataclasses import dataclass
from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Vehicle:
    id: int
    registration: str
    make: str
    model: str
    year: int


@dataclass(frozen=True, slots=True)
class MaintenanceJob:
    id: int
    vehicle_id: int
    description: str
    status: JobStatus
