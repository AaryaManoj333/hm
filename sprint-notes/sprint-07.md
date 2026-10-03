# Sprint 7 - Terminal application and Release 1 (Milestone 5, part 2)

**Goal:** let CityCare staff use everything from a menu, starting with sample data.

**Built**
- `hms/data/seed_data.py` - wards, doctors, nurses, patients, appointments and prescriptions as Python objects
- `hms/main.py` - 13 menu options + Exit; each option calls a `Hospital` method
- Error handling in the loop: `HospitalError` and `ValueError` -> `Error: <message>`; bad menu input -> `Invalid choice`
- README finished; `payroll.py` placeholder for Release 3

**Decisions**
- The menu has a small `ask_number()` helper so typing letters for an age gives "Age must be a whole number."
  instead of Python's technical message.
- The ICU is seeded full (4/4) so the "ward full" error can be demonstrated immediately.

**Fixed in this sprint:** a failed `Doctor`/`Nurse` (bad specialisation or shift) used to consume an ID;
the doctor-only checks now run before `super().__init__()`.

**Tests:** `tests/test_main.py` runs the real menu with fake keyboard input (`unittest.mock`) - 93 tests in total.

**Release:** tag `<your-name>-v1.0`.

**Next:** Release 2 (advanced scenarios) - starts with replacing the OutPatient/InPatient subclasses by composition.
