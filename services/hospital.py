from hms.exceptions.exceptions import (
    DoctorNotAvailableError, DoctorNotFoundError, InvalidOperationError,
    PatientNotFoundError, WardFullError,
)
from hms.models.medicine import Prescription
from hms.models.patient import InPatient
from hms.models.person import Person
from hms.services.appointment import Appointment, AppointmentStatus
from hms.services.billing import Bill


def print_all(items):
    """Print get_details() for every item in the list.

    There is no isinstance() check anywhere: patients, doctors, nurses and even an
    Ambulance all work, because each one has its own get_details() (polymorphism).
    """
    for item in items:
        print(item.get_details())


class Hospital:
    """Owns all the data and provides every hospital operation.

    The menu in main.py only calls these methods - it never touches the lists directly.
    """

    # Stored once on the class, so every object shares the same name.
    NAME = "CityCare Hospital"

    def __init__(self):
        self.patients = []
        self.doctors = []
        self.nurses = []
        self.wards = {}          # ward type -> Ward, e.g. {"ICU": Ward(...)}
        self.appointments = []
        self.bills = []

    # ------------------------------------------------------------------ adding
    def add_ward(self, ward):
        self.wards[ward.ward_type] = ward
        return ward

    def add_doctor(self, doctor):
        self.doctors.append(doctor)
        return doctor

    def add_nurse(self, nurse):
        self.nurses.append(nurse)
        return nurse

    @staticmethod
    def is_valid_phone(phone):
        """True for exactly 10 digits (the same rule Person uses)."""
        return Person.is_valid_phone(phone)

    def register_patient(self, patient):
        self.patients.append(patient)
        return patient

    # ----------------------------------------------------------------- finding
    def find_patient(self, patient_id):
        wanted = patient_id.strip().upper()          # "p003" works like "P003"
        for patient in self.patients:
            if patient.person_id == wanted:
                return patient
        raise PatientNotFoundError(f"Patient {wanted} not found.")

    def find_doctor(self, doctor_id):
        wanted = doctor_id.strip().upper()
        for doctor in self.doctors:
            if doctor.person_id == wanted:
                return doctor
        raise DoctorNotFoundError(f"Doctor {wanted} not found.")

    def find_ward(self, ward_type):
        wanted = ward_type.strip().lower()           # "icu" works like "ICU"
        for name, ward in self.wards.items():
            if name.lower() == wanted:
                return ward
        raise InvalidOperationError(f"Unknown ward type '{ward_type}'. Choose General, Private or ICU.")

    def find_appointment(self, appointment_id):
        wanted = appointment_id.strip().upper()
        for appointment in self.appointments:
            if appointment.appointment_id == wanted:
                return appointment
        raise InvalidOperationError(f"Appointment {wanted} not found.")

    def search_patient(self, text):
        """Search by exact ID or by part of the name (not case sensitive)."""
        text = text.strip().lower()
        found = [patient for patient in self.patients
                 if text == patient.person_id.lower() or (text and text in patient.name.lower())]
        if not found:
            raise PatientNotFoundError(f"No patient found for '{text}'.")
        return found

    # ------------------------------------------------------------ appointments
    def free_slots(self, doctor):
        """The doctor's slots that are not already booked."""
        return [slot for slot in doctor.available_slots if not self._slot_taken(doctor, slot)]

    def _slot_taken(self, doctor, slot):
        return any(a.doctor is doctor and a.slot == slot and a.status == AppointmentStatus.SCHEDULED
                   for a in self.appointments)

    def book_appointment(self, patient_id, doctor_id, slot):
        patient = self.find_patient(patient_id)
        doctor = self.find_doctor(doctor_id)
        slot = slot.strip()
        if slot not in doctor.available_slots or self._slot_taken(doctor, slot):
            raise DoctorNotAvailableError(f"Dr. {doctor.name} is not available at {slot}.")
        appointment = Appointment(patient, doctor, slot)
        self.appointments.append(appointment)
        return appointment

    def cancel_appointment(self, appointment_id):
        appointment = self.find_appointment(appointment_id)
        if appointment.status == AppointmentStatus.COMPLETED:
            raise InvalidOperationError("A completed appointment cannot be cancelled.")
        if appointment.status == AppointmentStatus.CANCELLED:
            raise InvalidOperationError("This appointment is already cancelled.")
        appointment.status = AppointmentStatus.CANCELLED
        return appointment

    def complete_appointment(self, appointment_id):
        appointment = self.find_appointment(appointment_id)
        if appointment.status == AppointmentStatus.CANCELLED:
            raise InvalidOperationError("A cancelled appointment cannot be completed.")
        appointment.status = AppointmentStatus.COMPLETED
        return appointment

    # --------------------------------------------------------------- admission
    def admit_patient(self, patient_id, ward_type):
        patient = self.find_patient(patient_id)
        if not isinstance(patient, InPatient):
            raise InvalidOperationError(
                f"{patient.name} is an outpatient and cannot be admitted. Register an inpatient (IPD) instead.")
        if patient.is_admitted:
            raise InvalidOperationError(f"{patient.name} is already admitted.")
        ward = self.find_ward(ward_type)
        if ward.is_full():
            raise WardFullError(
                f"{ward.ward_type} ward is full ({ward.occupied_beds()}/{ward.total_beds} beds occupied).")
        bed_number = ward.assign_bed(patient)
        patient.admit(ward, bed_number)
        return patient

    def discharge_patient(self, patient_id):
        patient = self.find_patient(patient_id)
        if not isinstance(patient, InPatient):
            raise InvalidOperationError(f"{patient.name} is an outpatient and cannot be discharged.")
        if not patient.is_admitted:
            raise InvalidOperationError(f"{patient.name} is not currently admitted.")
        patient.ward.free_bed(patient)
        patient.discharge()
        return patient

    # ----------------------------------------------------------- prescriptions
    def add_prescription(self, patient_id, doctor_id, medicines):
        patient = self.find_patient(patient_id)
        doctor = self.find_doctor(doctor_id)
        if not medicines:
            raise InvalidOperationError("A prescription needs at least one medicine.")
        prescription = Prescription(doctor, patient, medicines)
        patient.prescriptions.append(prescription)
        return prescription

    # ----------------------------------------------------------------- billing
    def _attending_doctor(self, patient):
        """The doctor on the patient's latest prescription, else on their latest appointment."""
        if patient.prescriptions:
            return patient.prescriptions[-1].doctor
        booked = [a for a in self.appointments
                  if a.patient is patient and a.status != AppointmentStatus.CANCELLED]
        return booked[-1].doctor if booked else None

    def generate_bill(self, patient_id):
        patient = self.find_patient(patient_id)
        doctor = self._attending_doctor(patient)
        if doctor is None:
            raise InvalidOperationError(
                f"No doctor visit recorded for {patient.name}. Book an appointment or add a prescription first.")
        if isinstance(patient, InPatient) and patient.ward is None:
            raise InvalidOperationError(f"{patient.name} has never been admitted, so there is no stay to bill.")
        visits = len([a for a in self.appointments
                      if a.patient is patient and a.status != AppointmentStatus.CANCELLED])
        items = patient.get_bill_items(doctor.consultation_fee, max(1, visits))
        bill = Bill(patient, items)
        self.bills.append(bill)
        return bill

    def bills_sorted(self):
        """All bills, highest amount first."""
        return sorted(self.bills, reverse=True)      # uses Bill.__lt__

    # ----------------------------------------------------------------- reports
    def ward_occupancy(self):
        """List of (ward type, occupied beds, total beds)."""
        return [(ward.ward_type, len(ward), ward.total_beds) for ward in self.wards.values()]   # len(ward) = Ward.__len__
