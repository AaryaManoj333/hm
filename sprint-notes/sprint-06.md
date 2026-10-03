# Sprint 6 - Usability of objects (Milestone 5, part 1)

**Goal:** make the objects pleasant to print, compare, sort and create.

**Built**
- `__str__` (for people) and `__repr__` (for developers) on Patient, Doctor, Appointment
- `__eq__` + `__hash__` on Person, `__len__` + `__contains__` on Ward, `__lt__` + `__add__` on Bill
- `@classmethod Patient.from_string(...)`, `@staticmethod Hospital.is_valid_phone(...)`
- `Hospital.bills_sorted()` now uses `sorted(bills)`; ward occupancy uses `len(ward)`

**Bug found and fixed**
- Giving `Ward` a `__len__` makes an empty ward behave like `False`. `Nurse.get_details()` used
  `if self.assigned_ward`, so a nurse in an empty ward showed "not assigned". Fixed with `is not None`
  and added a test.

**Decisions**
- Defining `__eq__` removes the default `__hash__`, so `__hash__` is defined from the ID.
- `Patient.from_string` on the base class returns an `OutPatient` (a plain `Patient` cannot be billed).

**Tests:** `tests/test_usability.py`

**Next sprint:** sample data, the terminal menu, README and the Release 1 tag.
