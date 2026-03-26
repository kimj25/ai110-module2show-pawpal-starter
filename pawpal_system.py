from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    description: str
    category: str
    due_time: str
    is_completed: bool = False

    def mark_complete(self):
        pass


@dataclass
class Schedule:
    date: date
    tasks: list = field(default_factory=list)

    def get_pending(self):
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: list = field(default_factory=list)
    schedule: Schedule = None

    def add_health_note(self, note):
        pass

    def get_summary(self):
        pass


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: list = []

    def add_pet(self, pet_obj):
        pass

    def get_all_tasks(self):
        pass
