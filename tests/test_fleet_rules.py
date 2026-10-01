import pytest

from fleetops.application.fleet import FleetValidationError, validate_job, validate_vehicle


def test_vehicle_rules_accept_complete_vehicle() -> None:
    validate_vehicle("ABC-123", "Volvo", "FH", 2022)


@pytest.mark.parametrize("year", [1949, 2101])
def test_vehicle_rules_reject_out_of_range_year(year: int) -> None:
    with pytest.raises(FleetValidationError, match="year"):
        validate_vehicle("ABC-123", "Volvo", "FH", year)


def test_job_rules_reject_blank_description() -> None:
    with pytest.raises(FleetValidationError, match="description"):
        validate_job(1, "  ")
