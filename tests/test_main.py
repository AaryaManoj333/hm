import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from hms.data.seed_data import load_sample_data
from hms.main import main
from hms.models.person import Person
from hms.services.appointment import Appointment
from hms.services.billing import Bill
from hms.services.hospital import Hospital


def run_menu(*answers):
    """Run the real menu with fake keyboard input and return everything it printed."""
    output = io.StringIO()
    with patch("builtins.input", side_effect=list(answers)), redirect_stdout(output):
        main()
    return output.getvalue()


class MenuTestCase(unittest.TestCase):
    def setUp(self):
        Person.reset_counters()
        Appointment._counter = 0
        Bill._counter = 0


class TestSampleData(MenuTestCase):
    def test_meets_the_minimum_sample_data(self):
        hospital = Hospital()
        load_sample_data(hospital)
        self.assertGreaterEqual(len(hospital.doctors), 3)
        self.assertGreaterEqual(len(hospital.nurses), 2)
        self.assertGreaterEqual(len(hospital.wards), 3)
        self.assertGreaterEqual(len(hospital.patients), 5)


class TestSampleInteraction(MenuTestCase):
    def test_booking_conflict_and_full_icu(self):
        text = run_menu("6", "P003", "D001", "11:00",
                        "6", "P005", "D001", "11:00",
                        "8", "P002", "ICU",
                        "0")
        self.assertIn("Available slots for Dr. Meera Rao (Cardiology): 10:00, 11:00, 15:00", text)
        self.assertIn("Appointment A004 booked for Anil Kumar with Dr. Meera Rao at 11:00.", text)
        self.assertIn("Error: Dr. Meera Rao is not available at 11:00.", text)
        self.assertIn("Error: ICU ward is full (4/4 beds occupied).", text)


class TestInputHandling(MenuTestCase):
    def test_bad_menu_input_shows_invalid_choice_and_redisplays_menu(self):
        text = run_menu("abc", "99", "", "-1", "0")
        self.assertEqual(text.count("Invalid choice"), 4)
        self.assertEqual(text.count("===== CityCare Hospital Management System ====="), 5)

    def test_ids_work_in_lowercase(self):
        self.assertIn("Anil Kumar", run_menu("5", "p003", "0"))

    def test_bad_age_does_not_crash(self):
        text = run_menu("1", "OPD", "Test", "abc", "0")
        self.assertIn("Error: Age must be a whole number.", text)

    def test_bad_phone_gives_a_clear_message(self):
        text = run_menu("1", "OPD", "Test", "30", "M", "123", "O+", "0")
        self.assertIn("Error: Phone number must be exactly 10 digits.", text)

    def test_unknown_patient(self):
        self.assertIn("Error: Patient P999 not found.", run_menu("11", "P999", "0"))

    def test_discharging_an_outpatient(self):
        text = run_menu("9", "P001", "0")
        self.assertIn("Error: Ravi Kumar is an outpatient and cannot be discharged.", text)

    def test_cancelling_twice(self):
        text = run_menu("7", "A001", "7", "A001", "0")
        self.assertIn("Appointment A001 cancelled.", text)
        self.assertIn("Error: This appointment is already cancelled.", text)

    def test_bad_specialisation_does_not_use_up_an_id(self):
        text = run_menu("2", "D", "Dr Test", "40", "M", "9000000000", "Dentistry", "500", "10:00",
                        "2", "D", "Dr Test", "40", "M", "9000000000", "General", "500", "10:00",
                        "0")
        self.assertIn("Error: Specialisation must be one of", text)
        self.assertIn("Doctor added: D005", text)


class TestWholeWorkflow(MenuTestCase):
    def test_register_ipd_admit_prescribe_bill_discharge(self):
        text = run_menu(
            "1", "IPD", "Asha Roy", "30", "F", "9000000001", "o+", "General",      # P010, admitted
            "10", "P010", "D001", "Aspirin", "75 mg", "2", "",                      # prescription
            "11", "P010",                                                           # bill
            "9", "P010",                                                            # discharge
            "13",                                                                   # bills list
            "12",                                                                   # occupancy
            "0")
        self.assertIn("Registered Asha Roy with ID P010 (IPD).", text)
        self.assertIn("Asha Roy admitted to General ward, bed 2.", text)
        self.assertIn("Prescription saved for Asha Roy", text)
        # 1 day stay (1000) + doctor 800 + medicines 100 = 1900, +5% tax = 1995
        self.assertIn("Rs   1,995.00", text)
        self.assertIn("Asha Roy discharged from General ward", text)
        self.assertIn("B001 | Asha Roy (P010) | Rs 1,995.00", text)
        self.assertIn("ICU      4/4 beds occupied (100%)", text)

    def test_outpatient_bill_after_booking(self):
        text = run_menu("6", "P003", "D001", "11:00", "11", "P003", "13", "0")
        self.assertIn("Rs     800.00", text)       # consultation fee only


if __name__ == "__main__":
    unittest.main()
