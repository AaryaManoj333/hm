import io
import unittest
from contextlib import redirect_stdout

from hms.models.ambulance import Ambulance
from hms.models.patient import OutPatient, InPatient
from hms.models.person import Person
from hms.models.staff import Doctor, SeniorDoctor, Nurse, Receptionist
from hms.models.ward import Ward
from hms.services.hospital import print_all


class TestPolymorphism(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()

    def test_print_all_shows_a_mixed_list(self):
        icu = Ward("ICU", 4, 8000)
        patient = OutPatient("Ravi", 34, "M", "9876543210", "O+")
        inpatient = InPatient("Sita", 62, "F", "9876543211", "A+")
        inpatient.admit(icu, icu.assign_bed(inpatient))
        doctor = Doctor("Meera Rao", 45, "F", "9876543212", "Cardiology", 800, ["10:00", "11:00"])
        senior = SeniorDoctor("Kavita", 55, "F", "9876543213", "General", 1000)
        nurse = Nurse("Priya", 29, "F", "9876543214", "Night", icu)
        desk = Receptionist("Anu", 25, "F", "9876543215")
        ambulance = Ambulance("AMB01", "KA-01-1234", "Raju", "ALS")

        output = io.StringIO()
        with redirect_stdout(output):
            print_all([patient, inpatient, doctor, senior, nurse, desk, ambulance])
        lines = output.getvalue().splitlines()

        self.assertEqual(len(lines), 7)
        self.assertIn("[Patient] P001 | Ravi", lines[0])
        self.assertIn("ICU ward, bed 1", lines[1])
        self.assertIn("Dr. Meera Rao | Cardiology", lines[2])
        self.assertIn("[Senior Doctor]", lines[3])
        self.assertIn("Night shift | Ward: ICU", lines[4])
        self.assertIn("[Receptionist]", lines[5])
        self.assertIn("[Ambulance] AMB01", lines[6])

    def test_each_class_has_its_own_role(self):
        self.assertEqual(Doctor("A", 40, "M", "9876543210", "General", 500).get_role(), "Doctor")
        self.assertEqual(SeniorDoctor("A", 40, "M", "9876543210", "General", 500).get_role(), "Senior Doctor")
        self.assertEqual(Nurse("A", 30, "F", "9876543210", "Morning").get_role(), "Nurse")


if __name__ == "__main__":
    unittest.main()
