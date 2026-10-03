"""Terminal menu for the CityCare Hospital Management System.

This file only talks to the user. Every menu option calls a Hospital method;
the lists inside Hospital are never touched here.

Run it from the project folder with:  python -m hms.main
"""
from hms.data.seed_data import load_sample_data
from hms.exceptions.exceptions import HospitalError
from hms.models.medicine import Medicine
from hms.models.patient import InPatient, OutPatient
from hms.models.staff import Doctor, Nurse
from hms.services.hospital import Hospital, print_all

MENU = f"""
===== {Hospital.NAME} Management System =====
 1. Register patient (OPD / IPD)
 2. Add doctor / nurse
 3. View all doctors
 4. View all patients
 5. Search patient by ID or name
 6. Book appointment
 7. Cancel appointment
 8. Admit patient to ward
 9. Discharge patient
10. Add prescription
11. Generate bill
12. View ward occupancy
13. View all bills (sorted by amount)
 0. Exit"""


# ---------------------------------------------------------------- small helpers
def ask(prompt):
    return input(prompt).strip()


def ask_number(prompt, field):
    """Ask for a whole number; a friendly ValueError is raised for anything else."""
    try:
        return int(ask(prompt))
    except ValueError:
        raise ValueError(f"{field} must be a whole number.")


def show_list(items, empty_message):
    if items:
        print_all(items)
    else:
        print(empty_message)


# ---------------------------------------------------------------- menu options
def register_patient_option(hospital):
    kind = ask("Patient type (OPD/IPD): ").upper()
    if kind not in ("OPD", "IPD"):
        raise ValueError("Patient type must be OPD or IPD.")
    name = ask("Name: ")
    age = ask_number("Age: ", "Age")
    gender = ask("Gender (M/F/O): ")
    phone = ask("Phone (10 digits): ")
    blood_group = ask("Blood group (e.g. O+): ").upper()

    patient_class = OutPatient if kind == "OPD" else InPatient
    patient = hospital.register_patient(patient_class(name, age, gender, phone, blood_group))
    print(f"Registered {patient.name} with ID {patient.person_id} ({kind}).")

    if kind == "IPD":
        ward_type = ask("Admit to a ward now? (General/Private/ICU, or press Enter to skip): ")
        if ward_type:
            show_admission(hospital.admit_patient(patient.person_id, ward_type))


def add_staff_option(hospital):
    kind = ask("Add Doctor or Nurse? (D/N): ").upper()
    if kind not in ("D", "N"):
        raise ValueError("Please choose D or N.")
    name = ask("Name: ")
    age = ask_number("Age: ", "Age")
    gender = ask("Gender (M/F/O): ")
    phone = ask("Phone (10 digits): ")

    if kind == "D":
        specialisation = ask("Specialisation (Cardiology/Orthopaedics/General/Paediatrics): ").title()
        fee = ask_number("Consultation fee (Rs): ", "Fee")
        slots = [slot.strip() for slot in ask("Available slots, comma separated (e.g. 10:00,11:00): ").split(",")
                 if slot.strip()]
        doctor = hospital.add_doctor(Doctor(name, age, gender, phone, specialisation, fee, slots))
        print(f"Doctor added: {doctor.person_id} - {doctor}.")
    else:
        shift = ask("Shift (Morning/Evening/Night): ").title()
        ward = hospital.find_ward(ask("Ward (General/Private/ICU): "))
        nurse = hospital.add_nurse(Nurse(name, age, gender, phone, shift, ward))
        print(f"Nurse added: {nurse.person_id} - {nurse.name}, {nurse.shift} shift, {ward.ward_type} ward.")


def view_doctors_option(hospital):
    show_list(hospital.doctors, "No doctors registered.")


def view_patients_option(hospital):
    show_list(hospital.patients, "No patients registered.")


def search_patient_option(hospital):
    text = ask("Enter patient ID or name: ")
    print_all(hospital.search_patient(text))


def book_appointment_option(hospital):
    patient_id = ask("Patient ID: ")
    doctor_id = ask("Doctor ID: ")
    doctor = hospital.find_doctor(doctor_id)
    free = hospital.free_slots(doctor)
    print(f"Available slots for {doctor}: {', '.join(free) if free else 'none'}")
    slot = ask("Choose slot: ")
    appointment = hospital.book_appointment(patient_id, doctor_id, slot)
    print(f"Appointment {appointment.appointment_id} booked for {appointment.patient.name} "
          f"with Dr. {appointment.doctor.name} at {appointment.slot}.")


def cancel_appointment_option(hospital):
    appointment = hospital.cancel_appointment(ask("Appointment ID: "))
    print(f"Appointment {appointment.appointment_id} cancelled.")


def show_admission(patient):
    print(f"{patient.name} admitted to {patient.ward.ward_type} ward, bed {patient.bed_number}.")


def admit_patient_option(hospital):
    patient_id = ask("Patient ID: ")
    ward_type = ask("Ward type (General/Private/ICU): ")
    show_admission(hospital.admit_patient(patient_id, ward_type))


def discharge_patient_option(hospital):
    patient = hospital.discharge_patient(ask("Patient ID: "))
    print(f"{patient.name} discharged from {patient.ward.ward_type} ward after "
          f"{patient.days_admitted()} day(s). Use option 11 to generate the bill.")


def add_prescription_option(hospital):
    patient_id = ask("Patient ID: ")
    doctor_id = ask("Doctor ID: ")
    medicines = []
    while True:
        name = ask("Medicine name (press Enter to finish): ")
        if not name:
            break
        dosage = ask("Dosage (e.g. 500 mg): ")
        days = ask_number("Number of days: ", "Days")
        medicines.append(Medicine(name, dosage, days))
    prescription = hospital.add_prescription(patient_id, doctor_id, medicines)
    print(f"Prescription saved for {prescription.patient.name}: {len(medicines)} medicine(s), "
          f"medicine cost Rs {prescription.total_charge()}.")


def generate_bill_option(hospital):
    print(hospital.generate_bill(ask("Patient ID: ")))


def ward_occupancy_option(hospital):
    for ward_type, occupied, total in hospital.ward_occupancy():
        percent = occupied / total * 100 if total else 0
        print(f"{ward_type:<8} {occupied}/{total} beds occupied ({percent:.0f}%)")


def view_bills_option(hospital):
    bills = hospital.bills_sorted()
    if not bills:
        print("No bills have been generated yet.")
    for bill in bills:
        print(f"{bill.bill_id} | {bill.patient.name} ({bill.patient.person_id}) | Rs {bill.total:,.2f}")


# ------------------------------------------------------------------- main loop
ACTIONS = {
    1: register_patient_option,
    2: add_staff_option,
    3: view_doctors_option,
    4: view_patients_option,
    5: search_patient_option,
    6: book_appointment_option,
    7: cancel_appointment_option,
    8: admit_patient_option,
    9: discharge_patient_option,
    10: add_prescription_option,
    11: generate_bill_option,
    12: ward_occupancy_option,
    13: view_bills_option,
}


def main():
    hospital = Hospital()
    load_sample_data(hospital)

    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        if not (choice.isascii() and choice.isdigit()) or int(choice) not in ACTIONS:
            print("Invalid choice. Please type a number from the menu.")
            continue

        try:
            ACTIONS[int(choice)](hospital)
        except (HospitalError, ValueError) as error:
            print(f"Error: {error}")          # friendly message, never a crash
        except Exception as error:            # safety net for anything unexpected
            print(f"Something went wrong: {error}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
