import unittest

from hms.models.medicine import Medicine
from hms.models.ward import Ward
from hms.services.hospital import Hospital


class TestMedicine(unittest.TestCase):
    def test_medicine_stores_values(self):
        medicine = Medicine("Paracetamol", "500 mg", 3)
        self.assertEqual(medicine.name, "Paracetamol")
        self.assertEqual(medicine.dosage, "500 mg")
        self.assertEqual(medicine.days, 3)

    def test_charge_is_50_per_day(self):
        self.assertEqual(Medicine("Paracetamol", "500 mg", 3).charge(), 150)

    def test_days_must_be_positive(self):
        with self.assertRaises(ValueError):
            Medicine("Paracetamol", "500 mg", 0)


class TestWard(unittest.TestCase):
    def test_new_ward_is_empty(self):
        ward = Ward("ICU", 4, 8000)
        self.assertEqual(ward.available_beds(), 4)
        self.assertFalse(ward.is_full())

    def test_ward_fills_up(self):
        ward = Ward("ICU", 2, 8000)
        ward.assign_bed("patient 1")
        ward.assign_bed("patient 2")
        self.assertEqual(ward.available_beds(), 0)
        self.assertTrue(ward.is_full())

    def test_free_bed_makes_room(self):
        ward = Ward("ICU", 1, 8000)
        patient = object()
        ward.assign_bed(patient)
        ward.free_bed(patient)
        self.assertFalse(ward.is_full())


class TestHospitalName(unittest.TestCase):
    def test_name_is_shared_class_attribute(self):
        self.assertEqual(Hospital.NAME, "CityCare Hospital")
        self.assertEqual(Hospital().NAME, Hospital.NAME)


if __name__ == "__main__":
    unittest.main()
