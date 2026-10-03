from abc import ABC, abstractmethod


class Person(ABC):
    """Base class for every person in the hospital.

    Person is abstract: you cannot create a plain Person, only a Patient, Doctor, Nurse ...

    age and phone are private (__age, __phone). They can only be read or changed
    through the properties below, which check the values first.
    """

    prefix = "X"     # every subclass sets its own letter: P, D, N, R
    _counters = {}   # class-level counter shared by all people: {"P": 3, "D": 1, ...}

    def __init__(self, name, age, gender, phone):
        # Validate first, so a bad person never uses up an ID.
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name cannot be empty.")
        self.name = name.strip()
        self.age = age          # goes through the age setter
        self.phone = phone      # goes through the phone setter
        self.gender = gender
        self.person_id = Person._next_id(self.prefix)

    # ----- contract: every type of person must provide these two methods -----
    @abstractmethod
    def get_details(self):
        """One line of text describing this person."""

    @abstractmethod
    def get_role(self):
        """The role as text, e.g. "Doctor"."""

    # ----- private age -----
    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, value):
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 120:
            raise ValueError("Age must be a whole number between 0 and 120.")
        self.__age = value

    # ----- private phone -----
    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        if not Person.is_valid_phone(value):
            raise ValueError("Phone number must be exactly 10 digits.")
        self.__phone = value

    @staticmethod
    def is_valid_phone(phone):
        """True only for a string of exactly 10 digits."""
        return isinstance(phone, str) and len(phone) == 10 and phone.isascii() and phone.isdigit()

    # ----- automatic IDs: P001, P002 ... D001 ... N001 ... -----
    @staticmethod
    def _next_id(prefix):
        number = Person._counters.get(prefix, 0) + 1
        Person._counters[prefix] = number
        return f"{prefix}{number:03d}"

    @staticmethod
    def reset_counters():
        """Start all ID counters again from 1 (used by the tests)."""
        Person._counters.clear()

    # ----- two people with the same ID are the same person -----
    def __eq__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return self.person_id == other.person_id

    def __hash__(self):
        return hash(self.person_id)   # needed because we defined __eq__
