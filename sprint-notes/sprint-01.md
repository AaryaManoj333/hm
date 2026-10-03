# Sprint 1 - Foundation and core entities (Milestone 1)

**Goal:** set up the repository and build the simplest entities.

**Built**
- Folder structure, README, .gitignore, project plan
- `Medicine` - name, dosage, days, `charge()` (Rs 50 per day)
- `Ward` - ward type, beds, daily charge, `available_beds()`, `is_full()`
- `Hospital.NAME` - one class attribute shared by everything

**Decisions**
- A ward keeps a dictionary `{bed number: patient}`; the number of free beds is calculated from it,
  so the count can never get out of sync with the real beds.

**Tests:** `tests/test_core.py`

**Next sprint:** the `Person` class with private, validated age and phone.
