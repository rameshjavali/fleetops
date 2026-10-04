import pytest

from fleetops.application.fleet import FleetValidationError, validate_job, validate_vehicle
from fleetops.domain.entities import JobStatus, MaintenanceJob, Vehicle


def test_domain_entities_represent_vehicle_and_maintenance_job() -> None:
    vehicle = Vehicle(id=1, registration="ABC-123", make="Volvo", model="FH", year=2022)
    job = MaintenanceJob(
        id=1,
        vehicle_id=vehicle.id,
        description="Inspect brakes",
        status=JobStatus.QUEUED,
    )

    assert vehicle.registration == "ABC-123"
    assert job.vehicle_id == vehicle.id
    assert job.status is JobStatus.QUEUED


def test_vehicle_rules_accept_complete_vehicle() -> None:
    validate_vehicle("ABC-123", "Volvo", "FH", 2022)


@pytest.mark.parametrize(("make", "model"), [("", "FH"), ("Volvo", " ")])
def test_vehicle_rules_reject_blank_make_or_model(make: str, model: str) -> None:
    with pytest.raises(FleetValidationError, match="make and model"):
        validate_vehicle("ABC-123", make, model, 2022)


@pytest.mark.parametrize("year", [1950, 2100])
def test_vehicle_rules_accept_year_boundaries(year: int) -> None:
    validate_vehicle("ABC-123", "Volvo", "FH", year)


@pytest.mark.parametrize("year", [1949, 2101])
def test_vehicle_rules_reject_out_of_range_year(year: int) -> None:
    with pytest.raises(FleetValidationError, match="year"):
        validate_vehicle("ABC-123", "Volvo", "FH", year)


def test_job_rules_reject_invalid_vehicle_id() -> None:
    with pytest.raises(FleetValidationError, match="valid vehicle"):
        validate_job(0, "Inspect brakes")


def test_job_rules_reject_blank_description() -> None:
    with pytest.raises(FleetValidationError, match="description"):
        validate_job(1, "  ")


def test_job_rules_reject_long_description() -> None:
    with pytest.raises(FleetValidationError, match="at most 500"):
        validate_job(1, "x" * 501)
