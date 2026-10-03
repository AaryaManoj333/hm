import unittest
from datetime import date, timedelta

from hms.models.medicine import Medicine, Prescription
from hms.models.patient import OutPatient, InPatient
from hms.models.person import Person
from hms.models.staff import Doctor
from hms.models.ward import Ward


def prescribe(patient, doctor, *medicines):
    patient.prescriptions.append(Prescription(doctor, patient, medicines))


class TestBilling(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()
        self.doctor = Doctor("Meera Rao", 45, "F", "9876543212", "Cardiology", 800)

    def test_outpatient_bill(self):
        patient = OutPatient("Ravi", 34, "M", "9876543210", "O+")
        prescribe(patient, self.doctor, Medicine("A", "500 mg", 3), Medicine("B", "10 mg", 5))
        # 800 consultation + (50 x 3) + (50 x 5) = 1200
        self.assertEqual(patient.calculate_bill(doctor_fee=800), 1200)

    def test_senior_outpatient_gets_10_percent_off(self):
        patient = OutPatient("Old", 60, "M", "9876543210", "O+")
        self.assertEqual(patient.calculate_bill(doctor_fee=800), 720)

    def test_age_59_gets_no_discount(self):
        patient = OutPatient("Young", 59, "M", "9876543210", "O+")
        self.assertEqual(patient.calculate_bill(doctor_fee=800), 800)

    def _inpatient(self, age):
        ward = Ward("General", 5, 1000)
        patient = InPatient("Sita", age, "F", "9876543211", "A+")
        patient.admit(ward, 1, date.today() - timedelta(days=3))
        prescribe(patient, self.doctor, Medicine("A", "500 mg", 2))
        return patient

    def test_inpatient_bill_with_tax(self):
        patient = self._inpatient(40)
        # stay 3 x 1000 = 3000, doctor 500, medicines 100 -> 3600, tax 180 -> 3780
        self.assertEqual(patient.calculate_bill(doctor_fee=500), 3780)

    def test_senior_inpatient_discount_is_after_tax(self):
        patient = self._inpatient(70)
        # 3780 - 10% = 3402
        self.assertEqual(patient.calculate_bill(doctor_fee=500), 3402)

    def test_bill_items_add_up_to_the_total(self):
        patient = self._inpatient(70)
        items = patient.get_bill_items(doctor_fee=500)
        self.assertEqual(round(sum(amount for _, amount in items), 2), 3402)

    def test_bill_for_never_admitted_inpatient_fails(self):
        patient = InPatient("Sita", 40, "F", "9876543211", "A+")
        with self.assertRaises(ValueError):
            patient.calculate_bill(doctor_fee=500)

    def test_prescription_total(self):
        patient = OutPatient("Ravi", 34, "M", "9876543210", "O+")
        prescription = Prescription(self.doctor, patient, [Medicine("A", "1 mg", 2), Medicine("B", "1 mg", 4)])
        self.assertEqual(prescription.total_charge(), 300)


if __name__ == "__main__":
    unittest.main()
