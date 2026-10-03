class Ward:
    """A hospital ward (General, ICU or Private) with a fixed number of beds."""

    def __init__(self, ward_type, total_beds, charge_per_day):
        self.ward_type = ward_type
        self.total_beds = total_beds
        self.charge_per_day = charge_per_day
        self.beds = {}  # bed number -> patient who is using it

    def occupied_beds(self):
        return len(self.beds)

    def available_beds(self):
        return self.total_beds - len(self.beds)

    def is_full(self):
        return self.available_beds() == 0

    def assign_bed(self, patient):
        """Give the patient the first free bed and return the bed number."""
        for number in range(1, self.total_beds + 1):
            if number not in self.beds:
                self.beds[number] = patient
                return number
        return None  # ward is full

    def free_bed(self, patient):
        """Free the bed used by this patient."""
        for number, occupant in list(self.beds.items()):
            if occupant is patient:
                del self.beds[number]

    def __len__(self):
        """len(ward) is the number of occupied beds.
        Careful: this makes an EMPTY ward count as False in an `if`, so always write
        `if ward is None`, never `if ward`."""
        return len(self.beds)

    def __contains__(self, patient):
        """`patient in ward` is True when that patient is in one of the beds."""
        return any(occupant == patient for occupant in self.beds.values())
