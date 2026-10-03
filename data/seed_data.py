"""Sample data so CityCare staff can try the system immediately.

Everything is created as plain Python objects and added through Hospital methods.
"""
from datetime import date, timedelta

from hms.models.medicine import Medicine
from hms.models.patient import InPatient, OutPatient
from hms.models.staff import Doctor, Nurse, SeniorDoctor
from hms.models.ward import Ward


def load_sample_data(hospital):
    # ----- wards -----
    general = hospital.add_ward(Ward("General", 10, 1000))
    hospital.add_ward(Ward("Private", 5, 3500))
    icu = hospital.add_ward(Ward("ICU", 4, 8000))

    # ----- doctors (D001 - D004) -----
    hospital.add_doctor(Doctor("Meera Rao", 45, "F", "9876500001", "Cardiology", 800,
                               ["10:00", "11:00", "15:00"]))
    hospital.add_doctor(Doctor("Arjun Mehta", 38, "M", "9876500002", "Orthopaedics", 700,
                               ["09:00", "12:00", "16:00"]))
    hospital.add_doctor(SeniorDoctor("Kavita Sharma", 55, "F", "9876500003", "General", 1000,
                                     ["09:30", "11:30", "14:00"]))
    hospital.add_doctor(Doctor("Rahul Verma", 41, "M", "9876500004", "Paediatrics", 600,
                               ["10:30", "13:30", "15:30"]))

    # ----- nurses (N001 - N002) -----
    hospital.add_nurse(Nurse("Priya Nair", 29, "F", "9876500011", "Morning", icu))
    hospital.add_nurse(Nurse("Suresh Babu", 34, "M", "9876500012", "Night", general))

    # ----- patients (P001 - P009) -----
    hospital.register_patient(OutPatient("Ravi Kumar", 34, "M", "9876500101", "O+"))     # P001
    hospital.register_patient(InPatient("Sita Devi", 62, "F", "9876500102", "A+"))       # P002 (waiting for a bed)
    hospital.register_patient(OutPatient("Anil Kumar", 45, "M", "9876500103", "B+"))     # P003
    hospital.register_patient(InPatient("Mohan Das", 70, "M", "9876500104", "AB-"))      # P004
    hospital.register_patient(OutPatient("Divya Nair", 28, "F", "9876500105", "O-"))     # P005
    hospital.register_patient(InPatient("Kiran Rao", 52, "M", "9876500106", "A-"))       # P006
    hospital.register_patient(InPatient("Latha Iyer", 41, "F", "9876500107", "B-"))      # P007
    hospital.register_patient(InPatient("Imran Khan", 36, "M", "9876500108", "AB+"))     # P008
    hospital.register_patient(InPatient("Meena Pillai", 59, "F", "9876500109", "O+"))    # P009

    hospital.find_patient("P004").medical_history.append("Hypertension")
    hospital.find_patient("P009").medical_history.append("Type 2 diabetes")

    # ----- admissions: the ICU is full (4 of 4 beds), General has 1 patient -----
    for patient_id, ward_type, days_ago in [("P004", "ICU", 4), ("P006", "ICU", 2),
                                            ("P007", "ICU", 1), ("P008", "ICU", 3),
                                            ("P009", "General", 5)]:
        patient = hospital.admit_patient(patient_id, ward_type)
        patient.admission_date = date.today() - timedelta(days=days_ago)

    # ----- appointments (A001 - A003) -----
    hospital.book_appointment("P001", "D002", "09:00")
    hospital.book_appointment("P004", "D003", "11:30")
    hospital.book_appointment("P009", "D003", "14:00")

    # ----- prescriptions for the inpatients -----
    hospital.add_prescription("P004", "D001", [Medicine("Aspirin", "75 mg", 5),
                                               Medicine("Atenolol", "50 mg", 5)])
    hospital.add_prescription("P006", "D003", [Medicine("Paracetamol", "500 mg", 3)])
    hospital.add_prescription("P007", "D003", [Medicine("Amoxicillin", "250 mg", 4)])
    hospital.add_prescription("P008", "D002", [Medicine("Ibuprofen", "400 mg", 3)])
    hospital.add_prescription("P009", "D003", [Medicine("Metformin", "500 mg", 7)])
