import unittest

from hms.models.patient import InPatient, OutPatient, Patient
from hms.models.person import Person
from hms.models.staff import Doctor, Nurse
from hms.models.ward import Ward
from hms.services.appointment import Appointment
from hms.services.billing import Bill
from hms.services.hospital import Hospital


class TestEquality(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()

    def test_same_id_means_equal(self):
        first = OutPatient("Ravi", 34, "M", "9876543210", "O+")
        Person.reset_counters()
        same_id = OutPatient("Someone Else", 20, "F", "9876543211", "A+")
        self.assertEqual(first, same_id)

    def test_different_ids_are_not_equal(self):
        a = OutPatient("A", 30, "M", "9876543210", "O+")
        b = OutPatient("B", 30, "M", "9876543210", "O+")
        self.assertNotEqual(a, b)
        self.assertEqual(len({a, b}), 2)    # still usable in a set

    def test_person_is_not_equal_to_other_types(self):
        patient = OutPatient("A", 30, "M", "9876543210", "O+")
        self.assertNotEqual(patient, "P001")


class TestTextForms(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()
        self.patient = OutPatient("Ravi Kumar", 34, "M", "9876543210", "O+")
        self.doctor = Doctor("Meera Rao", 45, "F", "9876543211", "Cardiology", 800, ["10:00"])

    def test_str(self):
        self.assertEqual(str(self.patient), "Ravi Kumar (P001, 34 yrs, OPD)")
        self.assertEqual(str(self.doctor), "Dr. Meera Rao (Cardiology)")

    def test_repr_shows_class_and_values(self):
        self.assertIn("OutPatient(person_id='P001'", repr(self.patient))
        self.assertIn("Doctor(person_id='D001'", repr(self.doctor))

    def test_appointment_str_and_repr(self):
        appointment = Appointment(self.patient, self.doctor, "10:00")
        self.assertIn("Ravi Kumar with Dr. Meera Rao at 10:00 [Scheduled]", str(appointment))
        self.assertIn("status=SCHEDULED", repr(appointment))


class TestWardMagicMethods(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()
        self.ward = Ward("ICU", 2, 8000)
        self.patient = InPatient("Sita", 62, "F", "9876543211", "A+")
        self.other = InPatient("Mohan", 50, "M", "9876543212", "B+")

    def test_len_counts_occupied_beds(self):
        self.assertEqual(len(self.ward), 0)
        self.ward.assign_bed(self.patient)
        self.assertEqual(len(self.ward), 1)

    def test_in_operator(self):
        self.ward.assign_bed(self.patient)
        self.assertIn(self.patient, self.ward)
        self.assertNotIn(self.other, self.ward)

    def test_nurse_with_an_empty_ward_still_shows_the_ward(self):
        nurse = Nurse("Priya", 29, "F", "9876543213", "Night", self.ward)
        self.assertIn("Ward: ICU", nurse.get_details())


class TestBillMagicMethods(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()
        patient = OutPatient("Ravi", 34, "M", "9876543210", "O+")
        self.small = Bill(patient, [("Consultation", 500)])
        self.large = Bill(patient, [("Consultation", 900), ("Medicines", 100)])

    def test_less_than_and_sorting(self):
        self.assertTrue(self.small < self.large)
        self.assertEqual(sorted([self.large, self.small]), [self.small, self.large])

    def test_add_returns_combined_amount(self):
        self.assertEqual(self.small + self.large, 1500)

    def test_unsupported_add(self):
        with self.assertRaises(TypeError):
            self.small + 5


class TestClassAndStaticMethods(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()

    def test_from_string(self):
        patient = Patient.from_string("Ravi,34,M,9876543210,O+")
        self.assertEqual(patient.name, "Ravi")
        self.assertEqual(patient.age, 34)
        self.assertEqual(patient.blood_group, "O+")
        self.assertIsInstance(patient, OutPatient)      # walk-in registration

    def test_from_string_on_a_subclass_uses_that_subclass(self):
        self.assertIsInstance(InPatient.from_string("Sita,62,F,9876543211,A+"), InPatient)

    def test_from_string_bad_input(self):
        for bad in ("Ravi,34,M", "Ravi,abc,M,9876543210,O+", "Ravi,34,M,123,O+"):
            with self.assertRaises(ValueError):
                Patient.from_string(bad)

    def test_is_valid_phone_static_method(self):
        self.assertTrue(Hospital.is_valid_phone("9876543210"))
        self.assertFalse(Hospital.is_valid_phone("12345"))
        self.assertFalse(Hospital().is_valid_phone("98765432ab"))


if __name__ == "__main__":
    unittest.main()
