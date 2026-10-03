from enum import Enum


class AppointmentStatus(Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Appointment:
    """Links one patient, one doctor and one time slot."""

    _counter = 0   # class-level counter for A001, A002 ...

    def __init__(self, patient, doctor, slot):
        Appointment._counter += 1
        self.appointment_id = f"A{Appointment._counter:03d}"
        self.patient = patient
        self.doctor = doctor
        self.slot = slot
        self.status = AppointmentStatus.SCHEDULED

    def __str__(self):
        return (f"Appointment {self.appointment_id}: {self.patient.name} with Dr. {self.doctor.name} "
                f"at {self.slot} [{self.status.value}]")

    def __repr__(self):
        return (f"Appointment(appointment_id={self.appointment_id!r}, patient={self.patient.person_id!r}, "
                f"doctor={self.doctor.person_id!r}, slot={self.slot!r}, status={self.status.name})")
