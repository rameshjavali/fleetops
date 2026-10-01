from dataclasses import dataclass


@dataclass(slots=True)
class FleetValidationError(ValueError):
    message: str

    def __str__(self) -> str:
        return self.message


def validate_vehicle(registration: str, make: str, model: str, year: int) -> None:
    if not registration.strip():
        raise FleetValidationError("Registration is required.")
    if not make.strip() or not model.strip():
        raise FleetValidationError("Vehicle make and model are required.")
    if year < 1950 or year > 2100:
        raise FleetValidationError("Vehicle year must be between 1950 and 2100.")


def validate_job(vehicle_id: int, description: str) -> None:
    if vehicle_id < 1:
        raise FleetValidationError("A valid vehicle is required.")
    if not description.strip():
        raise FleetValidationError("Job description is required.")
    if len(description) > 500:
        raise FleetValidationError("Job description must be at most 500 characters.")
