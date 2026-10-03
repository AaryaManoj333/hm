# Sprint 3 - People hierarchy (Milestone 2)

**Goal:** build every kind of person on top of `Person`.

**Built**
- `Patient(Person)` -> `OutPatient`, `InPatient` (single and multilevel inheritance)
- `Doctor(Person)` -> `SeniorDoctor` (multilevel inheritance)
- `Nurse`, `Receptionist`
- Each class sets its own `prefix` ("P", "D", "N", "R"); `SeniorDoctor` and `OutPatient` reuse their parent's letter

**Decisions**
- `InPatient` keeps its own `admit()` / `discharge()` / `days_admitted()` so the hospital code stays short.
- A stay of less than a day counts as 1 day (a bed was used).

**Tests:** `tests/test_people.py`

**Next sprint:** polymorphism (`get_details`, `print_all`), abstract base classes and billing rules.
