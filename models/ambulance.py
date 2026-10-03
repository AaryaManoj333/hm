class Ambulance:
    """An ambulance is NOT a person, but it has get_details() just like one,
    so print_all() can show it in the same list."""

    def __init__(self, ambulance_id, vehicle_number, driver_name, ambulance_type="Basic"):
        self.ambulance_id = ambulance_id
        self.vehicle_number = vehicle_number
        self.driver_name = driver_name
        self.ambulance_type = ambulance_type
        self.status = "Available"

    def get_details(self):
        return (f"[Ambulance] {self.ambulance_id} | {self.vehicle_number} | "
                f"Driver: {self.driver_name} | {self.ambulance_type} | {self.status}")
