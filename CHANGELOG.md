# Changelog

## Sprint 1 - Foundation and core entities
- Added folder structure, README and .gitignore
- Added docs/project-plan.md
- Added `Medicine` (with charge per day)
- Added `Ward` with `available_beds()` and `is_full()`
- Added `Hospital.NAME` shared class attribute

## Sprint 2 - Data protection and validation
- Added `Person` with private `__age` and `__phone` (properties with validation)
- Age must be 0-120, phone must be exactly 10 digits; both raise `ValueError` with a clear message
- Added automatic IDs with a class-level counter (P001, D001, N001 ...)

## Sprint 3 - People hierarchy
- Added `Patient`, `OutPatient`, `InPatient` (ward, bed number, admission date)
- Added `Doctor` (specialisation, fee, slots), `SeniorDoctor` (can approve discharges), `Nurse`, `Receptionist`
- All subclasses call `super().__init__()` so validation and IDs are inherited

## Sprint 4 - Uniform behaviour, contracts and billing
- `Person` is now an abstract class (`get_details()`, `get_role()`) - it cannot be created directly
- Every person type has its own `get_details()` and `get_role()`
- Added `print_all()` - works on a mixed list without any `isinstance` check
- Added `Ambulance` (not a person, but has `get_details()`)
- Added abstract `Billable`; `OutPatient` and `InPatient` implement `calculate_bill()`
- Billing rules: OPD fee + medicines; IPD stay + doctor fee + medicines + 5% tax; 10% senior discount after tax
- Added `Prescription` (needed for medicine charges)

## Sprint 5 - Hospital operations and error handling
- Added `Appointment` and `AppointmentStatus` enum (SCHEDULED, COMPLETED, CANCELLED)
- Added `Bill` (ID, patient, line items, total)
- Added `Hospital` with register_patient, book_appointment, cancel_appointment, admit_patient,
  discharge_patient, add_prescription, generate_bill, search_patient and more
- Added custom exceptions: `HospitalError` base with PatientNotFound, DoctorNotAvailable, WardFull, InvalidOperation
  (and one extra, DoctorNotFound, for unknown doctor IDs)

## Sprint 6 - Usability of objects
- `__str__` and `__repr__` for `Patient`, `Doctor` and `Appointment`
- `Person.__eq__` (same ID = equal) and `__hash__`
- `Ward.__len__` (occupied beds) and `Ward.__contains__` (`patient in ward`)
- `Bill.__lt__` (sort bills) and `Bill.__add__` (combined amount)
- `Patient.from_string()` class method and `Hospital.is_valid_phone()` static method
- Fix: `Nurse.get_details()` no longer treats an empty ward as "no ward"

## Sprint 7 - Terminal application
- Added sample data (`hms/data/seed_data.py`): 4 doctors, 2 nurses, 3 wards, 9 patients, 3 appointments
- Added the menu-driven terminal application (`hms/main.py`) with all 13 options
- Invalid menu input shows "Invalid choice"; every custom exception is shown as `Error: <message>`
- IDs are accepted in any case
- Fix: a doctor or nurse with an invalid specialisation or shift no longer uses up an ID
- Added end-to-end menu tests (`tests/test_main.py`)
- Completed README (how to run, module-to-principle table, billing rules, assumptions)

## Release 1.0
All nine Release 1 modules delivered: core entities, data protection, people hierarchy, uniform behaviour,
contracts, hospital operations, error handling, usability of objects and the terminal application.
