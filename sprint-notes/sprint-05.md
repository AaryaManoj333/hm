# Sprint 5 - Hospital operations and error handling (Milestone 4)

**Goal:** one `Hospital` class that owns the data and every operation, with clear errors.

**Built**
- `Appointment` with a status Enum, `Bill` with line items, `Hospital` with all operations
- `exceptions/exceptions.py`: `HospitalError` and its subclasses, raised from `Hospital` methods
- IDs are accepted in any case (`p003` = `P003`)

**Decisions**
- A booked slot only blocks other bookings while the appointment is SCHEDULED, so cancelling frees the slot.
- The doctor on a bill is the doctor of the latest prescription, otherwise of the latest appointment.
- An outpatient cannot be admitted (it raises `InvalidOperationError`): admissions are for inpatients.
- Added one extra exception, `DoctorNotFoundError`, because "slot taken" and "no such doctor" are different problems.

**Tests:** `tests/test_hospital.py`

**Next sprint:** magic methods, `from_string` and `is_valid_phone`.
