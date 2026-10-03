class Bill:
    """A bill: an ID, the patient and a list of line items [(description, amount), ...]."""

    _counter = 0   # class-level counter for B001, B002 ...

    def __init__(self, patient, items):
        Bill._counter += 1
        self.bill_id = f"B{Bill._counter:03d}"
        self.patient = patient
        self.items = list(items)

    @property
    def total(self):
        return round(sum(amount for _, amount in self.items), 2)

    def __str__(self):
        lines = [f"Bill {self.bill_id} - {self.patient.name} ({self.patient.person_id})"]
        for description, amount in self.items:
            lines.append(f"  {description:<48} Rs {amount:>10,.2f}")
        lines.append(f"  {'TOTAL':<48} Rs {self.total:>10,.2f}")
        return "\n".join(lines)

    def __lt__(self, other):
        """Lets us sort bills by total: sorted(bills)."""
        if not isinstance(other, Bill):
            return NotImplemented
        return self.total < other.total

    def __add__(self, other):
        """bill1 + bill2 gives the combined amount (a number)."""
        if not isinstance(other, Bill):
            return NotImplemented
        return round(self.total + other.total, 2)
