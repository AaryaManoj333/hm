import unittest
from datetime import date, timedelta

from hms.exceptions.exceptions import (
    DoctorNotAvailableError, HospitalError, InvalidOperationError,
    PatientNotFoundError, WardFullError,
)
from hms.models.medicine import Medicine
from hms.models.patient import InPatient, OutPatient
from hms.models.person import Person
from hms.models.staff import Doctor
from hms.models.ward import Ward
from hms.services.appointment import AppointmentStatus
from hms.services.hospital import Hospital


class HospitalTestCase(unittest.TestCase):
    """Builds a small hospital that every test below starts from."""

    def setUp(self):
        Person.reset_counters()
        self.hospital = Hospital()
        self.hospital.add_ward(Ward("General", 2, 1000))
        self.hospital.add_ward(Ward("ICU", 1, 8000))
        self.doctor = self.hospital.add_doctor(
            Doctor("Meera Rao", 45, "F", "9876543200", "Cardiology", 800, ["10:00", "11:00"]))
        self.opd = self.hospital.register_patient(OutPatient("Anil Kumar", 45, "M", "9876543201", "B+"))
        self.ipd = self.hospital.register_patient(InPatient("Sita Devi", 62, "F", "9876543202", "A+"))
        self.ipd2 = self.hospital.register_patient(InPatient("Mohan Das", 50, "M", "9876543203", "O+"))


class TestSearching(HospitalTestCase):
    def test_find_patient_any_case(self):
        self.assertIs(self.hospital.find_patient("p001"), self.opd)

    def test_unknown_patient(self):
        with self.assertRaises(PatientNotFoundError):
            self.hospital.find_patient("P999")

    def test_search_by_id_and_partial_name(self):
        self.assertEqual(self.hospital.search_patient("P002"), [self.ipd])
        self.assertEqual(self.hospital.search_patient("kumar"), [self.opd])

    def test_search_with_no_match(self):
        with self.assertRaises(PatientNotFoundError):
            self.hospital.search_patient("nobody")


class TestAppointments(HospitalTestCase):
    def test_book_appointment(self):
        appointment = self.hospital.book_appointment("P001", "D001", "11:00")
        self.assertEqual(appointment.appointment_id[0], "A")
        self.assertEqual(appointment.status, AppointmentStatus.SCHEDULED)

    def test_slot_already_taken(self):
        self.hospital.book_appointment("P001", "D001", "11:00")
        with self.assertRaises(DoctorNotAvailableError):
            self.hospital.book_appointment("P002", "D001", "11:00")

    def test_slot_not_in_doctors_list(self):
        with self.assertRaises(DoctorNotAvailableError) as context:
            self.hospital.book_appointment("P001", "D001", "23:00")
        self.assertIn("not available at 23:00", str(context.exception))

    def test_free_slots_shrink_after_booking(self):
        self.hospital.book_appointment("P001", "D001", "10:00")
        self.assertEqual(self.hospital.free_slots(self.doctor), ["11:00"])

    def test_cancel_frees_the_slot(self):
        appointment = self.hospital.book_appointment("P001", "D001", "10:00")
        self.hospital.cancel_appointment(appointment.appointment_id)
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)
        self.hospital.book_appointment("P002", "D001", "10:00")   # works again

    def test_cannot_cancel_completed_or_cancelled(self):
        first = self.hospital.book_appointment("P001", "D001", "10:00")
        self.hospital.complete_appointment(first.appointment_id)
        with self.assertRaises(InvalidOperationError):
            self.hospital.cancel_appointment(first.appointment_id)
        second = self.hospital.book_appointment("P002", "D001", "11:00")
        self.hospital.cancel_appointment(second.appointment_id)
        with self.assertRaises(InvalidOperationError):
            self.hospital.cancel_appointment(second.appointment_id)


class TestAdmission(HospitalTestCase):
    def test_admit_and_discharge(self):
        self.hospital.admit_patient("P002", "general")
        self.assertTrue(self.ipd.is_admitted)
        self.assertEqual(self.hospital.wards["General"].available_beds(), 1)
        self.hospital.discharge_patient("P002")
        self.assertFalse(self.ipd.is_admitted)
        self.assertEqual(self.hospital.wards["General"].available_beds(), 2)

    def test_ward_full(self):
        self.hospital.admit_patient("P002", "ICU")
        with self.assertRaises(WardFullError) as context:
            self.hospital.admit_patient("P003", "ICU")
        self.assertEqual(str(context.exception), "ICU ward is full (1/1 beds occupied).")
        self.assertFalse(self.ipd2.is_admitted)

    def test_outpatient_cannot_be_admitted_or_discharged(self):
        with self.assertRaises(InvalidOperationError):
            self.hospital.admit_patient("P001", "General")
        with self.assertRaises(InvalidOperationError):
            self.hospital.discharge_patient("P001")

    def test_cannot_admit_twice_or_discharge_when_not_admitted(self):
        self.hospital.admit_patient("P002", "General")
        with self.assertRaises(InvalidOperationError):
            self.hospital.admit_patient("P002", "General")
        with self.assertRaises(InvalidOperationError):
            self.hospital.discharge_patient("P003")

    def test_unknown_ward(self):
        with self.assertRaises(InvalidOperationError):
            self.hospital.admit_patient("P002", "Garden")


class TestPrescriptionsAndBills(HospitalTestCase):
    def test_prescription_is_kept_on_the_patient(self):
        self.hospital.add_prescription("P001", "D001", [Medicine("Aspirin", "75 mg", 4)])
        self.assertEqual(len(self.opd.prescriptions), 1)

    def test_empty_prescription_rejected(self):
        with self.assertRaises(InvalidOperationError):
            self.hospital.add_prescription("P001", "D001", [])

    def test_outpatient_bill(self):
        self.hospital.book_appointment("P001", "D001", "10:00")
        self.hospital.add_prescription("P001", "D001", [Medicine("Aspirin", "75 mg", 4)])
        bill = self.hospital.generate_bill("P001")
        self.assertEqual(bill.total, 800 + 200)   # fee + 50 x 4 days

    def test_inpatient_bill(self):
        self.hospital.admit_patient("P002", "General")
        self.ipd.admission_date = date.today() - timedelta(days=2)
        self.hospital.add_prescription("P002", "D001", [Medicine("Aspirin", "75 mg", 2)])
        bill = self.hospital.generate_bill("P002")
        # stay 2000 + doctor 800 + medicines 100 = 2900, +5% = 3045, senior (62) -10% = 2740.5
        self.assertEqual(bill.total, 2740.5)

    def test_bill_for_unknown_patient(self):
        with self.assertRaises(PatientNotFoundError):
            self.hospital.generate_bill("P404")

    def test_bill_without_doctor_visit(self):
        with self.assertRaises(InvalidOperationError):
            self.hospital.generate_bill("P001")

    def test_bill_for_never_admitted_inpatient(self):
        self.hospital.add_prescription("P002", "D001", [Medicine("Aspirin", "75 mg", 2)])
        with self.assertRaises(InvalidOperationError):
            self.hospital.generate_bill("P002")

    def test_bills_sorted_highest_first(self):
        self.hospital.add_prescription("P001", "D001", [Medicine("A", "1 mg", 1)])
        self.hospital.add_prescription("P003", "D001", [Medicine("A", "1 mg", 10)])
        self.hospital.admit_patient("P003", "General")
        small = self.hospital.generate_bill("P001")
        large = self.hospital.generate_bill("P003")
        self.assertEqual(self.hospital.bills_sorted(), [large, small])


class TestOneBaseException(HospitalTestCase):
    def test_all_errors_can_be_caught_as_hospital_error(self):
        for action in (
            lambda: self.hospital.find_patient("P999"),
            lambda: self.hospital.find_doctor("D999"),
            lambda: self.hospital.admit_patient("P001", "ICU"),
            lambda: self.hospital.book_appointment("P001", "D001", "03:00"),
        ):
            with self.assertRaises(HospitalError):
                action()

    def test_ward_occupancy_report(self):
        self.hospital.admit_patient("P002", "ICU")
        self.assertIn(("ICU", 1, 1), self.hospital.ward_occupancy())


if __name__ == "__main__":
    unittest.main()
