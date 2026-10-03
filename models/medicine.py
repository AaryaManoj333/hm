from datetime import date


class Medicine:
    """One medicine on a prescription: name, dosage (e.g. "500 mg") and number of days."""

    CHARGE_PER_DAY = 50  # rupees per medicine per day

    def __init__(self, name, dosage, days):
        if days <= 0:
            raise ValueError("Days must be greater than 0.")
        self.name = name
        self.dosage = dosage
        self.days = days

    def charge(self):
        """Cost of this medicine for the whole course."""
        return Medicine.CHARGE_PER_DAY * self.days


class Prescription:
    """A doctor's prescription for one patient: a list of Medicine objects."""

    def __init__(self, doctor, patient, medicines):
        self.doctor = doctor
        self.patient = patient
        self.medicines = list(medicines)
        self.date = date.today()

    def total_charge(self):
        return sum(medicine.charge() for medicine in self.medicines)
