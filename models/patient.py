from abc import ABC, abstractmethod
from datetime import date

from hms.models.person import Person

SERVICE_TAX_RATE = 0.05     # 5% service tax on inpatient bills
SENIOR_AGE = 60             # senior citizen = 60 or older
SENIOR_DISCOUNT = 0.10      # 10% off the final amount


class Billable(ABC):
    """Contract: anything that can be billed must know how to calculate its bill."""

    @abstractmethod
    def calculate_bill(self, doctor_fee=0, visits=1):
        """Return the final amount to pay."""


class Patient(Person):
    """A patient. OutPatient and InPatient are the two kinds of patient."""

    prefix = "P"
    patient_type = "Patient"

    def __init__(self, name, age, gender, phone, blood_group):
        super().__init__(name, age, gender, phone)
        self.blood_group = blood_group
        self.medical_history = []   # list of text notes
        self.prescriptions = []     # list of Prescription objects

    def get_role(self):
        return "Patient"

    def get_details(self):
        return (f"[{self.get_role()}] {self.person_id} | {self.name} | Age: {self.age} | "
                f"{self.gender} | Blood group: {self.blood_group} | {self.patient_type}")

    @classmethod
    def from_string(cls, text):
        """Quick registration: Patient.from_string("Ravi,34,M,9876543210,O+")."""
        parts = [part.strip() for part in text.split(",")]
        if len(parts) != 5:
            raise ValueError("Use the format: name,age,gender,phone,blood_group")
        name, age, gender, phone, blood_group = parts
        try:
            age = int(age)
        except ValueError:
            raise ValueError("Age must be a whole number.")
        # A plain Patient cannot be billed, so a quick walk-in registration becomes an OutPatient.
        patient_class = OutPatient if cls is Patient else cls
        return patient_class(name, age, gender, phone, blood_group)

    def __str__(self):
        return f"{self.name} ({self.person_id}, {self.age} yrs, {self.patient_type})"

    def __repr__(self):
        return (f"{type(self).__name__}(person_id={self.person_id!r}, name={self.name!r}, "
                f"age={self.age!r}, blood_group={self.blood_group!r})")

    def medicine_charges(self):
        """Rs 50 per medicine per day, over every prescription."""
        return sum(medicine.charge()
                   for prescription in self.prescriptions
                   for medicine in prescription.medicines)

    def add_senior_discount(self, items):
        """Add a 10% discount line (after tax) if the patient is 60 or older. Round all amounts."""
        total = sum(amount for _, amount in items)
        if self.age >= SENIOR_AGE:
            items.append(("Senior citizen discount (10%)", -total * SENIOR_DISCOUNT))
        return [(label, round(amount, 2)) for label, amount in items]


class OutPatient(Patient, Billable):
    """A patient who visits for a consultation and goes home (OPD)."""

    patient_type = "OPD"

    def get_bill_items(self, doctor_fee=0, visits=1):
        """OPD bill = consultation fee + medicine charges."""
        items = [
            ("Consultation fee", doctor_fee),
            ("Medicines", self.medicine_charges()),
        ]
        return self.add_senior_discount(items)

    def calculate_bill(self, doctor_fee=0, visits=1):
        return round(sum(amount for _, amount in self.get_bill_items(doctor_fee, visits)), 2)


class InPatient(Patient, Billable):
    """A patient who stays in a ward bed (IPD)."""

    patient_type = "IPD"

    def __init__(self, name, age, gender, phone, blood_group,
                 ward=None, bed_number=None, admission_date=None):
        super().__init__(name, age, gender, phone, blood_group)
        self.ward = ward
        self.bed_number = bed_number
        self.admission_date = admission_date
        self.discharge_date = None

    @property
    def is_admitted(self):
        return self.ward is not None and self.discharge_date is None

    def admit(self, ward, bed_number, admission_date=None):
        self.ward = ward
        self.bed_number = bed_number
        self.admission_date = admission_date or date.today()
        self.discharge_date = None

    def discharge(self, discharge_date=None):
        self.discharge_date = discharge_date or date.today()

    def days_admitted(self):
        """Number of days in hospital (a stay of less than one day counts as 1 day)."""
        if self.admission_date is None:
            return 0
        end = self.discharge_date or date.today()
        return max(1, (end - self.admission_date).days)

    def get_details(self):
        text = super().get_details()
        if self.is_admitted:
            return f"{text} | {self.ward.ward_type} ward, bed {self.bed_number}"
        return f"{text} | Not in a bed"

    def get_bill_items(self, doctor_fee=0, visits=1):
        """IPD bill = stay + doctor fee per visit + medicines, then 5% tax."""
        if self.ward is None:
            raise ValueError(f"{self.name} has never been admitted to a ward.")
        days = self.days_admitted()
        items = [
            (f"Ward stay: {days} day(s) x Rs {self.ward.charge_per_day} ({self.ward.ward_type})",
             days * self.ward.charge_per_day),
            (f"Doctor fee: {visits} visit(s) x Rs {doctor_fee}", doctor_fee * visits),
            ("Medicines", self.medicine_charges()),
        ]
        subtotal = sum(amount for _, amount in items)
        items.append(("Service tax (5%)", subtotal * SERVICE_TAX_RATE))
        return self.add_senior_discount(items)

    def calculate_bill(self, doctor_fee=0, visits=1):
        return round(sum(amount for _, amount in self.get_bill_items(doctor_fee, visits)), 2)
