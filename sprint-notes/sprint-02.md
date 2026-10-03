# Sprint 2 - Data protection and validation (Milestone 1)

**Goal:** make sure no invalid age or phone number can ever be stored.

**Built**
- `Person` with `person_id`, `name`, `age`, `gender`, `phone`
- `__age` and `__phone` are private; `@property` getters and setters check every value
- Automatic IDs: one class-level dictionary of counters, one letter per person type

**Decisions**
- The constructor assigns `self.age = age` (not `self.__age = age`) so the constructor
  and the setter use the same validation - the rule exists in only one place.
- Validation happens before the ID is generated, so a failed object does not waste an ID.

**Tests:** `tests/test_person.py`

**Next sprint:** the people hierarchy (Patient, Doctor, Nurse, Receptionist ...).
