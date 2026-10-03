# Sprint 4 - Uniform behaviour, contracts and billing (Milestone 3)

**Goal:** make all types usable through one interface and bill patients correctly.

**Built**
- Abstract `Person` (`abc.ABC`) and abstract `Billable`
- `get_details()` / `get_role()` in every person class; `Ambulance.get_details()`
- `print_all(items)` - polymorphism in action
- `OutPatient.calculate_bill()` and `InPatient.calculate_bill()` (different formulas)
- `Prescription` pulled forward from Module 6 because the bill needs the medicine list

**Decisions**
- A bill is a list of `(description, amount)` lines. `calculate_bill()` is just the sum of the lines,
  so the total can never disagree with the printed line items.
- The 10% senior discount is applied last (after tax). The IPD tax applies to the whole subtotal.
- `Patient` itself is not `Billable`; only the two real kinds of patient are.

**Tests:** `tests/test_polymorphism.py`, `tests/test_contracts.py`, `tests/test_billing.py`

**Next sprint:** `Appointment`, `Bill`, the `Hospital` class and custom exceptions.
