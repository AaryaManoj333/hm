import unittest
from datetime import date, timedelta

from hms.models.person import Person
from hms.models.patient import Patient, OutPatient, InPatient
from hms.models.staff import Doctor, SeniorDoctor, Nurse, Receptionist
from hms.models.ward import Ward


class TestPeopleHierarchy(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()

    def test_everyone_is_a_person(self):
        people = [
            OutPatient("A", 30, "M", "9876543210", "O+"),
            InPatient("B", 30, "F", "9876543211", "A+"),
            Doctor("C", 40, "F", "9876543212", "Cardiology", 800),
            SeniorDoctor("D", 50, "M", "9876543213", "General", 1000),
            Nurse("E", 28, "F", "9876543214", "Night"),
            Receptionist("F", 25, "F", "9876543215"),
        ]
        for person in people:
            self.assertIsInstance(person, Person)

    def test_ids_by_type(self):
        patient = OutPatient("A", 30, "M", "9876543210", "O+")
        inpatient = InPatient("B", 30, "F", "9876543211", "A+")
        doctor = Doctor("C", 40, "F", "9876543212", "Cardiology", 800)
        senior = SeniorDoctor("D", 50, "M", "9876543213", "General", 1000)
        nurse = Nurse("E", 28, "F", "9876543214", "Night")
        self.assertEqual(
            [patient.person_id, inpatient.person_id, doctor.person_id, senior.person_id, nurse.person_id],
            ["P001", "P002", "D001", "D002", "N001"],
        )

    def test_patient_fields(self):
        patient = OutPatient("A", 30, "M", "9876543210", "O+")
        self.assertEqual(patient.blood_group, "O+")
        self.assertEqual(patient.medical_history, [])

    def test_doctor_fields(self):
        doctor = Doctor("C", 40, "F", "9876543212", "Cardiology", 800, ["10:00", "11:00"])
        self.assertEqual(doctor.specialisation, "Cardiology")
        self.assertEqual(doctor.consultation_fee, 800)
        self.assertEqual(doctor.available_slots, ["10:00", "11:00"])

    def test_bad_specialisation_and_shift(self):
        with self.assertRaises(ValueError):
            Doctor("C", 40, "F", "9876543212", "Dentistry", 800)
        with self.assertRaises(ValueError):
            Nurse("E", 28, "F", "9876543214", "Afternoon")

    def test_only_senior_doctor_can_approve_discharge(self):
        doctor = Doctor("C", 40, "F", "9876543212", "Cardiology", 800)
        senior = SeniorDoctor("D", 50, "M", "9876543213", "General", 1000)
        self.assertFalse(doctor.can_approve_discharge)
        self.assertTrue(senior.can_approve_discharge)
        self.assertFalse(hasattr(doctor, "approve_discharge"))
        self.assertIn("approved", senior.approve_discharge(OutPatient("A", 30, "M", "9876543210", "O+")))

    def test_super_init_runs_validation_in_subclasses(self):
        with self.assertRaises(ValueError):
            Doctor("C", 500, "F", "9876543212", "Cardiology", 800)

    def test_inpatient_admit_and_discharge(self):
        ward = Ward("General", 5, 1000)
        patient = InPatient("B", 30, "F", "9876543211", "A+")
        self.assertFalse(patient.is_admitted)
        patient.admit(ward, 1, date.today() - timedelta(days=3))
        self.assertTrue(patient.is_admitted)
        self.assertEqual(patient.days_admitted(), 3)
        patient.discharge()
        self.assertFalse(patient.is_admitted)


if __name__ == "__main__":
    unittest.main()
