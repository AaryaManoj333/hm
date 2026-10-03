import unittest

from hms.models.person import Person


class Dummy(Person):
    """A tiny Person subclass, because Person is abstract and has its own ID letter per type."""
    prefix = "P"

    def get_details(self):
        return self.name

    def get_role(self):
        return "Dummy"


class TestPersonValidation(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()

    def test_valid_person(self):
        person = Dummy("Ravi", 34, "M", "9876543210")
        self.assertEqual(person.age, 34)
        self.assertEqual(person.phone, "9876543210")

    def test_age_is_private(self):
        person = Dummy("Ravi", 34, "M", "9876543210")
        self.assertFalse(hasattr(person, "__age"))
        self.assertEqual(person._Person__age, 34)   # name-mangled: hidden from normal use

    def test_age_limits(self):
        for bad_age in (-1, 121, "34", 3.5):
            with self.assertRaises(ValueError):
                Dummy("Ravi", bad_age, "M", "9876543210")
        Dummy("Newborn", 0, "F", "9876543210")
        Dummy("Oldest", 120, "F", "9876543210")

    def test_age_setter_validates(self):
        person = Dummy("Ravi", 34, "M", "9876543210")
        person.age = 35
        self.assertEqual(person.age, 35)
        with self.assertRaises(ValueError):
            person.age = 200
        self.assertEqual(person.age, 35)   # unchanged after the failure

    def test_phone_must_be_10_digits(self):
        for bad_phone in ("12345", "98765432101", "98765abcde", "", 9876543210):
            with self.assertRaises(ValueError):
                Dummy("Ravi", 34, "M", bad_phone)

    def test_error_messages_are_clear(self):
        with self.assertRaises(ValueError) as context:
            Dummy("Ravi", 34, "M", "123")
        self.assertIn("10 digits", str(context.exception))

    def test_name_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            Dummy("   ", 34, "M", "9876543210")


class TestAutomaticIds(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()

    def test_ids_count_up(self):
        first = Dummy("A", 20, "M", "9876543210")
        second = Dummy("B", 21, "F", "9876543211")
        self.assertEqual(first.person_id, "P001")
        self.assertEqual(second.person_id, "P002")

    def test_each_type_has_its_own_counter(self):
        class Doctor(Dummy):
            prefix = "D"
        Dummy("A", 20, "M", "9876543210")
        doctor = Doctor("B", 40, "F", "9876543211")
        self.assertEqual(doctor.person_id, "D001")

    def test_failed_object_does_not_use_an_id(self):
        with self.assertRaises(ValueError):
            Dummy("A", 999, "M", "9876543210")
        good = Dummy("B", 20, "M", "9876543210")
        self.assertEqual(good.person_id, "P001")

    def test_is_valid_phone(self):
        self.assertTrue(Person.is_valid_phone("9876543210"))
        self.assertFalse(Person.is_valid_phone("98765"))


if __name__ == "__main__":
    unittest.main()
