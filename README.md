# CityCare Hospital Management System (HMS)

Capstone 0 - Git and Python. A terminal application for CityCare Hospital's front desk, wards and
billing counter. Pure Python 3.10+, **standard library only**, object-oriented, no database and no
files: all data lives in Python objects (lists and dictionaries) in memory.

**Status:** Release 1 (v1.0) complete. Releases 2 and 3 are planned in `docs/project-plan.md`.

## How to run

You need Python 3.10 or newer. Nothing needs to be installed.

    cd "Capstone 0 - Git and Python"
    python -m hms.main

Run all the tests:

    python -m unittest discover -s tests -v

The system starts with sample data: 4 doctors (D001-D004), 2 nurses, 3 wards (General 10 beds,
Private 5 beds, ICU 4 beds), 9 patients (P001-P009) and 3 appointments (A001-A003).
The ICU starts **full**, so you can see `WardFullError` straight away.

Things to try:

| Do this | Expect |
|---------|--------|
| Option 6: patient `P003`, doctor `D001`, slot `11:00` | `Appointment A004 booked for Anil Kumar ...` |
| Option 6 again: patient `P005`, doctor `D001`, slot `11:00` | `Error: Dr. Meera Rao is not available at 11:00.` |
| Option 8: patient `P002`, ward `ICU` | `Error: ICU ward is full (4/4 beds occupied).` |
| Option 11: patient `P004` | Itemised IPD bill with 5% tax and the senior discount |
| Option 5: `p003` (lower case) | IDs work in any case |
| Menu input `abc` | `Invalid choice` and the menu is shown again |

## Project structure

    hms/
      main.py              terminal menu only (talks to the user, calls Hospital methods)
      models/              person.py, patient.py, staff.py, ward.py, medicine.py, ambulance.py
      services/            hospital.py, appointment.py, billing.py, payroll.py (Release 3)
      exceptions/          exceptions.py
      data/                seed_data.py (sample data as Python objects)
    tests/                 unittest scripts (standard library only)
    docs/                  project-plan.md and sprint-notes/

## Module -> design principle

| Module | What was built | Design principles used | Files |
|--------|----------------|------------------------|-------|
| 1 Core entities | `Medicine`, `Ward`, hospital name | Classes and objects; **class attribute** `Hospital.NAME` shared by all | `models/medicine.py`, `models/ward.py`, `services/hospital.py` |
| 2 Data protection | `Person` with private age and phone, auto IDs | **Encapsulation**: `__age`, `__phone` + `@property` getters/setters with validation; class-level counter | `models/person.py` |
| 3 People hierarchy | Patient, Doctor, Nurse, Receptionist, OutPatient, InPatient, SeniorDoctor | **Inheritance** (single and multilevel), `super().__init__()` | `models/patient.py`, `models/staff.py` |
| 4 Uniform behaviour | `get_details()`, `print_all()`, `calculate_bill()`, `Ambulance` | **Polymorphism** and duck typing: no `isinstance` in `print_all` | `services/hospital.py`, `models/*.py` |
| 5 Contracts | Abstract `Person`, abstract `Billable` | **Abstraction** with `abc.ABC` / `@abstractmethod` | `models/person.py`, `models/patient.py` |
| 6 Hospital operations | `Appointment` (Enum status), `Prescription`, `Bill`, `Hospital` | **Composition** (Hospital owns lists; an Appointment has a patient and a doctor), Enum | `services/*.py`, `models/medicine.py` |
| 7 Error handling | `HospitalError` and subclasses | **Custom exception hierarchy**; one `except HospitalError` catches all | `exceptions/exceptions.py` |
| 8 Usability | `__str__`, `__repr__`, `__eq__`, `__len__`, `__contains__`, `__lt__`, `__add__`, `from_string`, `is_valid_phone` | **Magic methods**, `@classmethod`, `@staticmethod` | `models/*.py`, `services/*.py` |
| 9 Terminal application | Menu loop, sample data | **Separation of concerns**: `main.py` has no business logic | `main.py`, `data/seed_data.py` |

## Billing rules

| Patient | Formula |
|---------|---------|
| OutPatient | doctor consultation fee + medicines (Rs 50 per medicine per day) |
| InPatient | (days admitted x ward charge per day) + doctor fee per visit + medicines, then **+5% service tax** |
| Age 60 or more | 10% discount on the final amount (after tax), for either type |

Ward charges: General Rs 1,000/day, Private Rs 3,500/day, ICU Rs 8,000/day.

A bill is stored as line items `(description, amount)`; the total is simply their sum, so the printed
lines and the total always agree.

## Design decisions and assumptions

- **Doctor on a bill:** the doctor of the patient's latest prescription, otherwise of their latest
  non-cancelled appointment. With no doctor visit recorded there is nothing to bill and the system says so.
- **"Doctor fee per visit" (inpatients):** fee x number of non-cancelled appointments (at least 1).
- **Days admitted:** a stay shorter than a day counts as 1 day. If the patient is still admitted, today is the end date.
- **Outpatients cannot be admitted** (`InvalidOperationError`); register an inpatient (IPD) instead.
  Converting OPD to IPD mid-visit is a Release 2 scenario and will need a redesign (composition).
- **Cancelling** an appointment frees its slot for other bookings.
- `Patient.from_string(...)` on the base class returns an `OutPatient`, because a plain `Patient` is not billable.
- One extra exception, `DoctorNotFoundError`, separates "no such doctor" from "slot not available".
- Money is printed as `Rs` (not the rupee sign) so it displays correctly in every terminal.
- Because `Ward` has `__len__`, an empty ward is "falsy" in Python - always write `ward is None`, never `if ward`.
  (This was a real bug found and fixed in Sprint 6.)

## Git workflow

- Repository: `GGTP_BLR_DP_SEP_26`, folder `Projects/Individual/<your-name>/Week 1/Capstone 0 - Git and Python/`
- One branch per sprint item: `<your-name>/sprint-01-person-validation`; merged into `main` through a pull request
- Commit messages: `type(scope): summary` with types `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- Tags: one per sprint (`<your-name>-sprint-01` ...) and per release (`<your-name>-v1.0`)
- Plan: `docs/project-plan.md` - history of changes: `CHANGELOG.md` - per-sprint notes: `docs/sprint-notes/`
