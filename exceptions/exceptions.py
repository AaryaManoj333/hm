class HospitalError(Exception):
    """Base class for every error raised by the hospital system."""


class PatientNotFoundError(HospitalError):
    """Searching or billing a patient ID that does not exist."""


class DoctorNotFoundError(HospitalError):
    """A doctor ID that does not exist."""


class DoctorNotAvailableError(HospitalError):
    """The slot is already taken, or is not in the doctor's list of slots."""


class WardFullError(HospitalError):
    """Admitting a patient into a ward that has no free bed."""


class InvalidOperationError(HospitalError):
    """An action that is not allowed, e.g. discharging an outpatient."""
