import unittest

from hms.models.patient import Billable, Patient, OutPatient, InPatient
from hms.models.person import Person


class TestAbstractClasses(unittest.TestCase):
    def test_cannot_create_a_plain_person(self):
        with self.assertRaises(TypeError):
            Person("Ravi", 34, "M", "9876543210")

    def test_cannot_create_a_plain_billable(self):
        with self.assertRaises(TypeError):
            Billable()

    def test_subclass_missing_a_method_cannot_be_created(self):
        class HalfDone(Person):
            def get_role(self):
                return "Half"   # get_details is missing
        with self.assertRaises(TypeError):
            HalfDone("A", 20, "M", "9876543210")

    def test_patients_are_billable(self):
        self.assertTrue(issubclass(OutPatient, Billable))
        self.assertTrue(issubclass(InPatient, Billable))
        self.assertFalse(issubclass(Patient, Billable))


if __name__ == "__main__":
    unittest.main()
