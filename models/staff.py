from hms.models.person import Person

SPECIALISATIONS = ("Cardiology", "Orthopaedics", "General", "Paediatrics")
SHIFTS = ("Morning", "Evening", "Night")


class Doctor(Person):
    prefix = "D"
    can_approve_discharge = False

    def __init__(self, name, age, gender, phone, specialisation, consultation_fee,
                 available_slots=None):
        # Check the doctor-only fields first, so a failed doctor does not use up an ID.
        if specialisation not in SPECIALISATIONS:
            raise ValueError("Specialisation must be one of: " + ", ".join(SPECIALISATIONS) + ".")
        if consultation_fee < 0:
            raise ValueError("Consultation fee cannot be negative.")
        super().__init__(name, age, gender, phone)
        self.specialisation = specialisation
        self.consultation_fee = consultation_fee
        self.available_slots = list(available_slots or [])   # e.g. ["10:00", "11:00"]

    def get_role(self):
        return "Doctor"

    def __str__(self):
        return f"Dr. {self.name} ({self.specialisation})"

    def __repr__(self):
        return (f"{type(self).__name__}(person_id={self.person_id!r}, name={self.name!r}, "
                f"specialisation={self.specialisation!r}, fee={self.consultation_fee!r})")

    def get_details(self):
        slots = ", ".join(self.available_slots) or "none"
        return (f"[{self.get_role()}] {self.person_id} | Dr. {self.name} | {self.specialisation} | "
                f"Fee: Rs {self.consultation_fee} | Slots: {slots}")


class SeniorDoctor(Doctor):
    """A doctor who also has the right to approve discharges."""

    can_approve_discharge = True

    def get_role(self):
        return "Senior Doctor"

    def approve_discharge(self, patient):
        return f"Discharge of {patient.name} approved by Dr. {self.name}."


class Nurse(Person):
    prefix = "N"

    def __init__(self, name, age, gender, phone, shift, assigned_ward=None):
        if shift not in SHIFTS:
            raise ValueError("Shift must be one of: " + ", ".join(SHIFTS) + ".")
        super().__init__(name, age, gender, phone)
        self.shift = shift
        self.assigned_ward = assigned_ward

    def get_role(self):
        return "Nurse"

    def get_details(self):
        ward = self.assigned_ward.ward_type if self.assigned_ward is not None else "not assigned"
        return (f"[{self.get_role()}] {self.person_id} | {self.name} | "
                f"{self.shift} shift | Ward: {ward}")


class Receptionist(Person):
    prefix = "R"

    def get_role(self):
        return "Receptionist"

    def get_details(self):
        return f"[{self.get_role()}] {self.person_id} | {self.name} | Phone: {self.phone}"
